# server/controllers/notas_credito_module.py
"""
Wrapper de compatibilidad para notas de crédito
Redirige a la nueva estructura
"""
from server.controllers.nota_credito_controller import NotaCreditoController
import logging

logger = logging.getLogger(__name__)

# Instanciar el nuevo controlador
_nota_credito_controller = NotaCreditoController()

def procesar_nota_credito(datos_validados):
    """Wrapper - procesa nota de crédito"""
    return _nota_credito_controller.procesar_documento(datos_validados)

def procesar_nota_credito_controller(datos):
    """Wrapper controller para procesamiento"""
    return _nota_credito_controller.procesar_controller(datos)
