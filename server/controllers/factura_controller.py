# server/controllers/factura_controller.py
"""
Controlador específico para facturas
"""
from server.controllers.base_controller import DocumentoBaseController
from server.schemas.factura_schema import FacturaSchema
import logging

logger = logging.getLogger(__name__)


class FacturaController(DocumentoBaseController):
    """
    Controlador específico para facturas
    """
    
    def __init__(self):
        super().__init__(FacturaSchema)
        self.tipo_documento = "FACTURA"
        # ✅ IMPORTANTE: No importar FacturaService aquí todavía
        self._factura_service = None
    
    @property
    def factura_service(self):
        """Propiedad que importa FacturaService solo cuando se necesita"""
        if self._factura_service is None:
            from server.services.factura_service import FacturaService  # ✅ Importación diferida
            self._factura_service = FacturaService()
        return self._factura_service
    
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
            'formas_pago': len(formas_pago)
        }
    
    def _procesar_cabecera_y_cliente(self, datos_validados):
        from server.controllers.helpers.create_invoice import cabeceraFacturas
        return cabeceraFacturas(datos_validados)
    
    def _procesar_pagos(self, factura_lines, datos_validados):
        from server.controllers.helpers.create_invoice import factura_pagos
        return factura_pagos(factura_lines, datos_validados)
    
    def procesar_documento(self, datos_validados):
        """Procesa una factura validada"""
        try:
            logger.info("🚀 Procesando factura...")
            resultado = self.factura_service.procesar_factura(datos_validados)  # ✅ Usa la propiedad
            logger.info("✅ Factura procesada exitosamente")
            return resultado
        except Exception as e:
            logger.error(f"❌ Error al procesar factura: {str(e)}")
            import traceback
            traceback.print_exc()
            raise