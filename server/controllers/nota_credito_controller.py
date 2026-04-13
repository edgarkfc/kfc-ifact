# server/controllers/nota_credito_controller.py
"""
Controlador específico para notas de crédito
"""
from server.controllers.base_controller import DocumentoBaseController
from server.schemas.nota_credito_schema import NotaCreditoSchema
from server.services.nota_credito_service import NotaCreditoService
import logging

logger = logging.getLogger(__name__)


class NotaCreditoController(DocumentoBaseController):
    """
    Controlador específico para notas de crédito
    """
    
    def __init__(self):
        super().__init__(NotaCreditoSchema)
        self.tipo_documento = "NOTA_CREDITO"
        self.nota_credito_service = NotaCreditoService()
    
    def _obtener_config_impresora(self, datos_validados):
        return datos_validados.get('config_impresora', {})
    
    def _obtener_resumen(self, datos_validados):
        cabecera = datos_validados.get('cabecera', {})
        cliente = datos_validados.get('cliente', {})
        detalle = datos_validados.get('detalle', [])
        formas_pago = datos_validados.get('formas_pago', [])
        
        return {
            'cliente': cliente.get('cliente_nombres', ''),
            'total_documento': cabecera.get('cabfact_total', 0),
            'items': len(detalle),
            'formas_pago': len(formas_pago),
            'tipo': 'NOTA_CREDITO'
        }
    
    def _procesar_cabecera_y_cliente(self, datos_validados):
        from server.controllers.helpers.create_invoice import cabeceraFacturas
        return cabeceraFacturas(datos_validados)
    
    def _procesar_pagos(self, factura_lines, datos_validados):
        from server.controllers.helpers.create_invoice import factura_pagos
        return factura_pagos(factura_lines, datos_validados)
    
    def procesar_documento(self, datos_validados):
        """Procesa una nota de crédito validada"""
        try:
            logger.info("🚀 Procesando nota de crédito...")
            resultado = self.nota_credito_service.procesar_nota_credito(datos_validados)
            logger.info("✅ Nota de crédito procesada exitosamente")
            return resultado
        except Exception as e:
            logger.error(f"❌ Error al procesar nota de crédito: {str(e)}")
            import traceback
            traceback.print_exc()
            raise