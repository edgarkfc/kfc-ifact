# validators/factura_validator.py
from marshmallow import Schema, fields, validates, ValidationError, validates_schema, EXCLUDE, pre_load, post_load, validate
import logging

logger = logging.getLogger(__name__)

# ============================================
# SCHEMA FORMA DE PAGO
# ============================================
class FormaPagoSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    formapagoactura_id = fields.Str(required=False, allow_none=True)
    formapago_id = fields.Str(required=True)
    cfac_id = fields.Str(required=False, allow_none=True)
    fpf_total_pagar = fields.Float(required=True)
    formapago = fields.Str(required=True)
    
    @validates('fpf_total_pagar')
    def validate_fpf_total_pagar(self, value, **kwargs):
        if value <= 0:
            raise ValidationError('El total a pagar debe ser mayor a 0')
        if value > 99999999.99: #ojo cammpo a validar si es necesario
            raise ValidationError('El total a pagar no puede ser mayor a 99999999.99')
        
        # Validar decimales (máximo 3)
        str_value = f"{value:.10f}".rstrip('0')
        if '.' in str_value:
            decimales = str_value.split('.')[-1]
            if len(decimales) > 3:
                raise ValidationError(f'Máximo 3 decimales permitidos (tiene {len(decimales)})')
    
    @validates('formapago')
    def validate_formapago_varchar4(self, value, **kwargs):
        if not isinstance(value, str):
            raise ValidationError('El campo debe ser un texto')
        if not (len(value) == 2 and value.isdigit()):
            raise ValidationError('El metodo de pago debe contener exactamente 2 dígitos numéricos')
         # Convertir a entero para validar rango
        numero = int(value)
        if numero < 1 or numero > 23:
            raise ValidationError('Metodo de pago no registrado, debe estar entre 01 y 23')


# ============================================
# SCHEMA DETALLE FACTURA
# ============================================
class DetalleFacturaSchema(Schema):
    class Meta:
        unknown = EXCLUDE
    
    detallefactura_id = fields.Str(required=True)
    dtfacplu_id = fields.Int(required=True)   
    dtfac_cantidad = fields.Float(
        required=True, 
        validate=validate.Range(min=0, error="La cantidad debe ser mayor a 0"),
        error_messages={"required": "La cantidad es obligatoria", "invalid": "Cantidad inválida"}
    )    
    dtfac_precio_unitario = fields.Float(
        required=True, 
        validate=validate.Range(min=0, error="El precio unitario debe ser mayor a 0"),
        error_messages={"required": "El precio unitario es obligatorio"}
    )    
    dtfac_iva = fields.Float(required=True, allow_none=True)    
    dtfac_total = fields.Float(
        required=True, 
        validate=validate.Range(min=0, error="El total debe ser mayor a 0"),
        error_messages={"required": "El total es obligatorio"}
    )
    aplicaImpuesto1 = fields.Int(required=False, allow_none=True)
    aplicaImpuesto2 = fields.Int(required=False, allow_none=True)
    aplicaImpuesto3 = fields.Int(required=False, allow_none=True)
    aplicaImpuesto4 = fields.Int(required=False, allow_none=True)
    aplicaImpuesto5 = fields.Int(required=False, allow_none=True)
    dtfac_valor_descuento = fields.Float(
        required=True, 
        validate=validate.Range(min=0, error="El valor del descuento debe ser mayor a 0"),
        error_messages={"required": "El valor del descuento es obligatorio"}
    )
    dtfac_porcentaje_descuento = fields.Int(
        required=True, 
        validate=validate.Range(
            min=0, 
            max=100, 
            error="El porcentaje de descuento debe estar entre 0% y 100%"
        ),
        error_messages={
            "required": "El porcentaje de descuento es obligatorio",
            "invalid": "El porcentaje debe ser un número entero",
            "null": "El porcentaje no puede ser nulo"
        }
    )
    dtfac_totaldesc = fields.Float(required=False, allow_none=True)
    dtfac_ivadesc = fields.Float(required=False, allow_none=True)
    dtfac_descripcion = fields.Str(required=True) # Descripción
    
    
# ============================================
# SCHEMA CLIENTE
# ============================================
class ClienteSchema(Schema):
    class Meta:
        unknown = EXCLUDE
    
    cliente_id = fields.Str(required=False, allow_none=True)
    cliente_documento = fields.Str(required=True)
    cliente_nombres = fields.Str(required=True)
    cliente_apellidos = fields.Str(required=False, allow_none=True)
    cliente_telefono = fields.Str(required=True)
    cliente_direccion = fields.Str(required=False, allow_none=False)
    cliente_email = fields.Str(required=False, allow_none=True)    
    
    @pre_load
    def clean_cli_direccion(self, data, **kwargs):
        """Convierte string 'null' a None"""
        if 'cliente_direccion' in data and data['cliente_direccion'] == 'null':
            data['cliente_direccion'] = None
        return data


# ============================================
# SCHEMA CABECERA FACTURA
# ============================================
class CabeceraFacturaSchema(Schema):
    class Meta:
        unknown = EXCLUDE
    
    cabfact_id = fields.Str(required=True)
    cabfact_nrofact_nc = fields.Str(required=False, allow_none=True)
    delivery_id = fields.Str(required=False)
    cabfact_fechacreacion = fields.Str(required=True)
    cabfact_subtotal = fields.Float(required=True)    
    cabfact_iva = fields.Float(required=True)
    cabfact_total = fields.Float(required=True)
    cabfact_valor_descuento = fields.Float(required=False, allow_none=False)    
    cabfact_porcentaje_descuento = fields.Int(
        required=True,
        validate=validate.Range(min=0, max=100, error="El porcentaje debe estar entre 1 y 100")
    )
    cabfact_tasa_conversion = fields.Float(required=True)   

# ============================================
# SCHEMA RESTAURANTE
# ============================================
class RestauranteSchema(Schema):
    class Meta:
        unknown = EXCLUDE
    
    restaurante = fields.Str(required=True)
    rest_id = fields.Int(required=True)
    impuesto_rest = fields.Bool(required=True, allow_none=False)
    nro_estacion = fields.Int(required=True)   

# ============================================
# SCHEMA PRINCIPAL FACTURA
# ============================================
class FacturaSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    restaurante = fields.Nested(RestauranteSchema, required=False)
    cabecera_factura = fields.Nested(CabeceraFacturaSchema, required=True)
    cliente = fields.Nested(ClienteSchema, required=True)
    detalle_factura = fields.List(fields.Nested(DetalleFacturaSchema), required=True)
    formas_pago = fields.List(fields.Nested(FormaPagoSchema), required=True)
    
    @pre_load
    def unwrap_factura(self, data, **kwargs):
        """Extrae el contenido de 'factura' si existe"""
        if isinstance(data, dict) and 'factura' in data:
            return data['factura']
        return data
    
    @validates_schema
    def validate_cross_fields(self, data, **kwargs):
        """Validaciones que cruzan múltiples campos"""
        errores = []
        
        # Validar que el total de formas_pago coincida con el total de cabecera
        if 'formas_pago' in data and 'cabecera_factura' in data:
            total_formas_pago = sum(fp.get('fpf_total_pagar', 0) for fp in data['formas_pago'])
            total_cabecera = data['cabecera_factura'].get('cabfact_total', 0)
            
            # Tolerancia de 0.01 por decimales
            if abs(total_formas_pago - total_cabecera) > 0.01:
                errores.append(
                    f'La suma de formas de pago ({total_formas_pago:.2f}) '
                    f'no coincide con el total de factura ({total_cabecera:.2f})'
                )
        
        # Validar que el subtotal + iva = total (aproximadamente)
        if 'cabecera_factura' in data:
            cab = data['cabecera_factura']
            calculado = cab.get('cabfact_subtotal', 0) + cab.get('cabfact_iva', 0) - cab.get('cabfact_valor_descuento', 0)
            if abs(calculado - cab.get('cabfact_total', 0)) > 0.01:
                errores.append(
                    f'El total calculado ({calculado:.2f}) no coincide '
                    f'con el total declarado ({cab.get("cabfact_total", 0):.2f})'
                )
        
        if errores:
            raise ValidationError(errores)
    
    @post_load
    def separate_data(self, data, **kwargs):
        """
        Separa los datos en categorías para facilitar su procesamiento
        """
        result = {
            'restaurante': data.get('restaurante'),
            'cabecera': data.get('cabecera_factura'),
            'cliente': data.get('cliente'),
            'detalle': data.get('detalle_factura', []),
            'formas_pago': data.get('formas_pago', []),
            'metadata': {
                'total_items': len(data.get('detalle_factura', [])),
                'total_formas_pago': len(data.get('formas_pago', [])),
                'total_factura': data.get('cabecera_factura', {}).get('cabfact_total'),
                'fecha': data.get('cabecera_factura', {}).get('cabfact_fechacreacion')
            }
        }
        return result