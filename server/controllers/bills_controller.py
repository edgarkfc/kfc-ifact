# server/controllers/bills_controller.py
"""
Wrapper de compatibilidad para facturas
Redirige a la nueva estructura
"""
from server.controllers.factura_controller import FacturaController
import logging

logger = logging.getLogger(__name__)

# Instanciar el nuevo controlador
_factura_controller = FacturaController()


def procesar_factura(datos_validados):
    """Wrapper - procesa factura"""
    return _factura_controller.procesar_documento(datos_validados)

def procesar_factura_controller(datos):
    """Wrapper controller para procesamiento"""
    return _factura_controller.procesar_controller(datos)
