# server/services/nota_credito_service.py
"""
Servicio de Nota de Crédito - Lógica de negocio para notas de crédito
"""
import logging
from typing import Dict, Any, List
from server.services.impresion_service import ImpresionService
from server.services.qr_service import QRService
from server.services.print_message_service import PrintMessageService

logger = logging.getLogger(__name__)


class NotaCreditoService:
    """Servicio para procesar notas de crédito"""
    
    def __init__(self):
        self.impresion_service = ImpresionService()
        self.qr_service = QRService()
        self.print_message_service = PrintMessageService()
    
    def procesar_nota_credito(self, datos_validados: Dict[str, Any]) -> Dict[str, Any]:
        """
        Procesa una nota de crédito validada y genera las líneas para impresión
        
        Args:
            datos_validados: Datos validados del schema
            
        Returns:
            Diccionario con la nota de crédito procesada
        """
        try:
            logger.info("🚀 Procesando nota de crédito...")
            
            # Extraer datos
            restaurante = datos_validados.get('restaurante', {})
            config_impresora = datos_validados.get('config_impresora', {})
            cabecera = datos_validados.get('cabecera', {})
            cliente = datos_validados.get('cliente', {})
            detalle = datos_validados.get('detalle', [])
            formas_pago = datos_validados.get('formas_pago', [])
            
            # Inicializar líneas
            nota_lines = []
            
            # 1. Generar cabecera
            tiene_delivery = 'delivery_id' in cabecera
            if cliente and cliente.get('cliente_nombres'):
                cabecera_lines = self.impresion_service.formatear_cabecera_con_cliente(
                    cliente, cabecera, tiene_delivery
                )
            else:
                cabecera_lines = self.impresion_service.formatear_cabecera_consumidor_final(
                    cabecera, tiene_delivery
                )
            nota_lines.extend(cabecera_lines)
            
            # 2. Procesar productos (como nota de crédito)
            productos_info = self._procesar_productos_nota_credito(detalle, restaurante)
            nota_lines.extend(productos_info['lineas'])
            
            # 3. Agregar separador
            nota_lines.append(self.impresion_service.agregar_linea_separador())
            
            # 4. Procesar pagos
            pagos_info = self._procesar_pagos_nota_credito(cabecera, formas_pago, config_impresora)
            nota_lines.extend(pagos_info['lineas'])
            
            # 5. Agregar línea final
            nota_lines.append(self.impresion_service.agregar_linea_final())
            
            # 6. Construir resultado
            resultado = {
                "tipo_documento": "NOTA_CREDITO",
                "cabecera_cliente": cabecera_lines,
                "detail_productos": {
                    "factura": productos_info['lineas'],
                    "subtotales": productos_info['subtotales']
                },
                "pagos_factura": pagos_info['lineas_pago'],
                "factura_unificada": nota_lines,
                "metadata": {
                    "total_items": len(detalle),
                    "total_pagos": len(formas_pago),
                    "factura_completa": len(nota_lines),
                    "total_nota": cabecera.get('cabfact_total', 0),
                    "subtotal": cabecera.get('cabfact_subtotal', 0),
                    "iva": cabecera.get('cabfact_iva', 0)
                }
            }
            
            logger.info("✅ Nota de crédito procesada exitosamente")
            return resultado
            
        except Exception as e:
            logger.error(f"❌ Error al procesar nota de crédito: {str(e)}")
            import traceback
            traceback.print_exc()
            raise
    
    def _procesar_productos_nota_credito(
        self, 
        detalle: List[Dict], 
        restaurante: Dict
    ) -> Dict[str, Any]:
        """Procesa los productos de la nota de crédito"""
        lineas = []
        subtotales = {
            'total_bruto': 0.0,
            'total_descuentos': 0.0,
            'total_iva': 0.0,
            'total_neto': 0.0
        }
        
        for producto in detalle:
            # Formatear línea del producto (es_nota_credito=True)
            linea, metadata = self.impresion_service.formatear_producto(
                producto, 
                es_nota_credito=True,  # Diferencia clave con factura
                restaurante=restaurante
            )
            lineas.append(linea)
            
            # Procesar descuentos (si aplican)
            if 'dtfac_porcentaje_descuento' in producto:
                porcentaje = producto.get('dtfac_porcentaje_descuento', 0)
                if porcentaje and float(porcentaje) != 0:
                    linea_dto = self.impresion_service.formatear_descuento_porcentaje(porcentaje)
                    if linea_dto:
                        lineas.append(linea_dto)
            
            if 'dtfac_valor_descuento' in producto:
                valor = producto.get('dtfac_valor_descuento', 0)
                if valor and float(valor) != 0:
                    linea_dto = self.impresion_service.formatear_descuento_monto(valor)
                    if linea_dto:
                        lineas.append(linea_dto)
            
            # Acumular subtotales
            subtotales['total_neto'] += float(producto.get('dtfac_total', 0) or 0)
        
        return {
            'lineas': lineas,
            'subtotales': subtotales
        }
    
    def _procesar_pagos_nota_credito(
        self,
        cabecera: Dict,
        formas_pago: List[Dict],
        config_impresora: Dict
    ) -> Dict[str, Any]:
        """Procesa los pagos de la nota de crédito"""
        lineas = []
        lineas_pago = []
        
        # Descuentos de cabecera
        descuento_porcentaje = cabecera.get('cabfact_porcentaje_descuento', 0)
        descuento_valor = cabecera.get('cabfact_valor_descuento', 0)
        
        # Validar QR
        impresion_qr = self.qr_service.validar_impresion_qr(
            config_impresora.get('impresion_qr', False)
        )
        
        if impresion_qr:
            datos_qr = self.qr_service.procesar_qr()
            if datos_qr:
                lineas.append(self.impresion_service.formatear_qr(datos_qr))
        
        # Descuentos
        if descuento_porcentaje and float(descuento_porcentaje) != 0:
            linea_dto = self.impresion_service.formatear_descuento_porcentaje(descuento_porcentaje)
            if linea_dto:
                lineas.append(linea_dto)
        
        if descuento_valor and float(descuento_valor) != 0:
            linea_dto = self.impresion_service.formatear_descuento_monto(descuento_valor)
            if linea_dto:
                lineas.append(linea_dto)
        
        # Pagos
        for pago in formas_pago:
            linea = self.impresion_service.formatear_pago(pago)
            lineas.append(linea)
            lineas_pago.append({
                'forma': pago.get('formapago'),
                'valor': pago.get('fpf_total_pagar', 0),
                'linea': linea
            })
        
        return {
            'lineas': lineas,
            'lineas_pago': lineas_pago
        }