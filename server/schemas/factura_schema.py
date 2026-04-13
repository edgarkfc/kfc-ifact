# server/schemas/factura_schema.py
"""
Schema de Factura - Migrado desde validators.py
"""
from marshmallow import Schema, fields, validates, ValidationError, validates_schema, EXCLUDE, pre_load, post_load
import logging
from decimal import Decimal, ROUND_HALF_UP

logger = logging.getLogger(__name__)

# Constantes
TOLERANCIA = 0.05

# Importar componentes
from server.schemas.componentes import (
    FormaPagoSchema,
    DetalleFacturaSchema,
    ClienteSchema,
    CabeceraFacturaSchema,
    RestauranteSchema,
    ConfigImpresoraSchema
)


class FacturaSchema(Schema):
    """Schema principal de factura"""
    class Meta:
        unknown = EXCLUDE

    restaurante = fields.Nested(RestauranteSchema, required=False)
    config_impresora = fields.Nested(ConfigImpresoraSchema, required=True)
    cabecera_factura = fields.Nested(CabeceraFacturaSchema, required=True)
    cliente = fields.Nested(ClienteSchema, required=True)
    detalle_factura = fields.List(fields.Nested(DetalleFacturaSchema), required=True)
    formas_pago = fields.List(fields.Nested(FormaPagoSchema), required=True)
    
    @pre_load
    def unwrap_factura(self, data, **kwargs):
        """Extrae el contenido de 'factura' si existe"""
        if isinstance(data, dict) and 'factura' in data:
            logger.debug("Desempaquetando campo 'factura'")
            return data['factura']
        return data
    
    def _calcular_totales_detalle(self, detalle_items):
        """Calcula los totales del detalle de factura"""
        subtotal_sin_iva = 0.0
        total_iva = 0.0
        total_con_iva = 0.0
        
        for item in detalle_items:
            cantidad = item.get('dtfac_cantidad', 0)
            precio_unitario = item.get('dtfac_precio_unitario', 0)
            iva_por_unidad = item.get('dtfac_iva', 0)
            total_declarado = item.get('dtfac_total', 0)
            
            if precio_unitario == 0:
                continue
            
            item_total = total_declarado
            item_iva = cantidad * iva_por_unidad
            item_subtotal_sin_iva = item_total - item_iva
            
            subtotal_sin_iva += item_subtotal_sin_iva
            total_iva += item_iva
            total_con_iva += item_total
        
        return {
            'subtotal_sin_iva': round(subtotal_sin_iva, 2),
            'total_iva': round(total_iva, 2),
            'total_con_iva': round(total_con_iva, 2)
        }
    
    @staticmethod
    def _round_to_2_decimals(value):
        """Redondea a 2 decimales usando el método HALF_UP"""
        return float(Decimal(str(value)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))
    
    @validates_schema
    def validate_cross_fields(self, data, **kwargs):
        """Validaciones que cruzan múltiples campos"""
        errores = []
        
        # Validar consistencia entre detalle y cabecera
        if data.get('detalle_factura') and data.get('cabecera_factura'):
            totales_detalle = self._calcular_totales_detalle(data['detalle_factura'])
            cab = data['cabecera_factura']
            
            total_cab = cab.get('cabfact_total', 0)
            
            if abs(totales_detalle['total_con_iva'] - total_cab) > TOLERANCIA:
                descuento_cab = cab.get('cabfact_valor_descuento', 0)
                total_con_descuento = totales_detalle['total_con_iva'] - descuento_cab
                if abs(total_con_descuento - total_cab) > TOLERANCIA:
                    errores.append(
                        f'El total del detalle ({totales_detalle["total_con_iva"]:.2f}) no coincide '
                        f'con el total de cabecera ({total_cab:.2f})'
                    )
        
        # Validar que el total de formas_pago coincida con el total de cabecera
        if data.get('formas_pago') and data.get('cabecera_factura'):
            total_formas_pago = sum(fp.get('fpf_total_pagar', 0) for fp in data['formas_pago'])
            total_cabecera = self._round_to_2_decimals(data['cabecera_factura'].get('cabfact_total', 0))
            total_formas_pago_rounded = self._round_to_2_decimals(total_formas_pago)
            
            if abs(total_formas_pago_rounded - total_cabecera) > TOLERANCIA:
                errores.append(
                    f'La suma de formas de pago ({total_formas_pago_rounded:.2f}) '
                    f'no coincide con el total de factura ({total_cabecera:.2f})'
                )
        
        if errores:
            raise ValidationError(errores)
    
    @post_load
    def separate_data(self, data, **kwargs):
        """Separa los datos en categorías para facilitar su procesamiento"""
        totales = self._calcular_totales_detalle(data.get('detalle_factura', []))
        
        return {
            'restaurante': data.get('restaurante'),
            'config_impresora': data.get('config_impresora'),
            'cabecera': data.get('cabecera_factura'),
            'cliente': data.get('cliente'),
            'detalle': data.get('detalle_factura', []),
            'formas_pago': data.get('formas_pago', []),
            'metadata': {
                'total_items': len(data.get('detalle_factura', [])),
                'total_formas_pago': len(data.get('formas_pago', [])),
                'total_factura': data.get('cabecera_factura', {}).get('cabfact_total'),
                'fecha': data.get('cabecera_factura', {}).get('cabfact_fechacreacion'),
                'subtotal_sin_iva': totales['subtotal_sin_iva'],
                'total_iva': totales['total_iva'],
                'total_con_iva': totales['total_con_iva']
            }
        }