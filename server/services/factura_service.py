# server/services/factura_service.py
"""
Servicio de Factura - Lógica de negocio para facturas
"""
import logging
from typing import Dict, Any, List, Optional
from server.services.impresion_service import ImpresionService
from server.services.validacion_service import ValidacionService
from server.services.qr_service import QRService
from server.controllers.helpers.print_messages import print_message
from server.services.impresion_fiscal_service import ImpresoraFiscalService

logger = logging.getLogger(__name__)


class FacturaService:
    """Servicio para procesar facturas (CON QR y mensajes)"""
    
    def __init__(self):
        self.impresion_service = ImpresionService()
        self.validacion_service = ValidacionService()
        self.qr_service = QRService()
        self.impresora_fiscal = ImpresoraFiscalService()

    def procesar_factura(self, datos_validados: Dict[str, Any]) -> Dict[str, Any]:
        """
        Procesa una factura validada y genera las líneas para impresión
        """
        try:
            logger.info("🚀 Procesando factura...")
            
            # Extraer datos
            restaurante = datos_validados.get('restaurante', {})
            config_impresora = datos_validados.get('config_impresora', {})
            cabecera = datos_validados.get('cabecera', {})
            cliente = datos_validados.get('cliente', {})
            detalle = datos_validados.get('detalle', [])
            formas_pago = datos_validados.get('formas_pago', [])
            
            # Inicializar líneas de factura
            factura_lines = []
            
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
            factura_lines.extend(cabecera_lines)
            
            # 2. Procesar productos
            productos_info = self._procesar_productos(detalle, restaurante)
            factura_lines.extend(productos_info['lineas'])
            
            # 3. Agregar separador
            factura_lines.append(self.impresion_service.agregar_linea_separador())
            
            # 4. Procesar pagos, QR y mensajes (INCLUYE QR Y MENSAJES)
            pagos_info = self._procesar_pagos(cabecera, formas_pago, config_impresora, cliente)
            factura_lines.extend(pagos_info['lineas'])
            
            # 5. Agregar línea final
            factura_lines.append(self.impresion_service.agregar_linea_final())
            
            # 6. Construir resultado
            resultado = {
                "tipo_documento": "FACTURA",
                "cabecera_cliente": cabecera_lines,
                "detail_productos": {
                    "factura": productos_info['lineas'],
                    "subtotales": productos_info['subtotales']
                },
                "pagos_factura": pagos_info['lineas_pago'],
                "factura_unificada": factura_lines,
                "metadata": {
                    "total_items": len(detalle),
                    "total_pagos": len(formas_pago),
                    "factura_completa": len(factura_lines),
                    "total_factura": cabecera.get('cabfact_total', 0),
                    "subtotal": cabecera.get('cabfact_subtotal', 0),
                    "iva": cabecera.get('cabfact_iva', 0)
                }
            }

            if self.impresora_fiscal.conectar():
                self.impresora_fiscal.imprimir_factura(resultado['factura_unificada'])
                self.impresora_fiscal.desconectar()
            
            logger.info("✅ Factura procesada exitosamente")
            return resultado
            
        except Exception as e:
            logger.error(f"❌ Error al procesar factura: {str(e)}")
            import traceback
            traceback.print_exc()
            raise
    
    def _procesar_productos(
        self, 
        detalle: List[Dict], 
        restaurante: Dict
    ) -> Dict[str, Any]:
        """Procesa los productos de la factura"""
        lineas = []
        subtotales = {
            'total_bruto': 0.0,
            'total_descuentos': 0.0,
            'total_iva': 0.0,
            'total_neto': 0.0
        }
        
        for producto in detalle:
            # Formatear línea del producto
            linea, metadata = self.impresion_service.formatear_producto(
                producto, 
                es_nota_credito=False,
                restaurante=restaurante
            )
            lineas.append(linea)
            
            # Procesar descuentos del producto
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
    
    def _procesar_pagos(
        self,
        cabecera: Dict,
        formas_pago: List[Dict],
        config_impresora: Dict,
        cliente: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Procesa los pagos de la factura (INCLUYE QR Y MENSAJES)"""
        lineas = []
        lineas_pago = []
        
        # ============================================
        # QR (impresion_qr)
        # ============================================
        if config_impresora.get('impresion_qr', False):
            try:
                # Preparar datos para QR
                datos_qr = {
                    'cabecera': cabecera,
                    'config_impresora': config_impresora
                }
                
                # Generar QR usando el servicio
                qr_resultado = self.qr_service.procesar_qr(datos_qr)
                
                if qr_resultado and qr_resultado.get('success') and qr_resultado.get('habilitado'):
                    # Obtener el texto del QR (formato: y1578408916)
                    qr_texto = qr_resultado.get('qr_texto', '')
                    
                    # SOLO LA TRAMA, sin formato adicional
                    lineas.append(qr_texto)
                    logger.info(f"✅ QR agregado a la FACTURA: {qr_texto}")
                else:
                    logger.warning("No se generó QR o está deshabilitado")
                    
            except Exception as e:
                logger.error(f"Error procesando QR en factura: {str(e)}")
        
        # ============================================
        # MENSAJES PERSONALIZADOS (impresion_msgqr)
        # Usando el helper print_messages
        # ============================================
        if config_impresora.get('impresion_msgqr', False):
            try:
                # Crear lista temporal para mensajes
                mensajes_tmp = []
                
                # Llamar al helper que obtiene mensajes desde BD
                resultado_msg = print_message(mensajes_tmp)
                
                # Obtener los mensajes agregados
                mensajes = resultado_msg.get('factura', [])
                
                # Agregar cada mensaje a las líneas
                for mensaje in mensajes:
                    
                    lineas.append(mensaje)
                    
                        
                
                logger.info(f"✅ Mensajes agregados: {len(mensajes)}")
                
            except Exception as e:
                logger.error(f"Error procesando mensajes: {str(e)}")
        
        # ============================================
        # DESCUENTOS DE CABECERA
        # ============================================
        descuento_porcentaje = cabecera.get('cabfact_porcentaje_descuento', 0)
        descuento_valor = cabecera.get('cabfact_valor_descuento', 0)
        
        if descuento_porcentaje and float(descuento_porcentaje) != 0:
            linea_dto = self.impresion_service.formatear_descuento_porcentaje(descuento_porcentaje)
            if linea_dto:
                lineas.append(linea_dto)
        
        if descuento_valor and float(descuento_valor) != 0:
            linea_dto = self.impresion_service.formatear_descuento_monto(descuento_valor)
            if linea_dto:
                lineas.append(linea_dto)
        
        # ============================================
        # PAGOS
        # ============================================
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