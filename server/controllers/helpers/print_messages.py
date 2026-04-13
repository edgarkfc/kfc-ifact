# server/controllers/helpers/print_messages.py
import logging
from typing import List, Dict, Any
from server.repositories.print_messages_repository import PrintMessagesRepository

logger = logging.getLogger(__name__)


def print_message(factura: List[str]) -> Dict[str, List[str]]:
    """
    Función que obtiene los mensajes activos y los agrega a la factura
    
    Args:
        factura: Lista de líneas de la factura existente
    
    Returns:
        Diccionario con la factura actualizada
    """
    try:
        # Crear instancia del repositorio
        print_messages_repo = PrintMessagesRepository()
        
        # Obtener mensajes activos y ordenados
        messages = print_messages_repo.get_all_active_ordered()
        
        # Agregar cada mensaje a la factura con el formato para impresora fiscal
        for message in messages:
            # Formato para la impresora fiscal: código + espacio + contenido + salto de línea
            line = f"{message.get('code', '')} {message.get('content', '')} \n"
            factura.append(line)
        
        logger.info(f"Se agregaron {len(messages)} mensajes a la factura")
        return {'factura': factura}
        
    except Exception as e:
        # Log del error como en la función PHP original
        logger.info(f"{str(e)} fn print_message, creando documento no fiscal para promo cupon / helper")
        # Devolver la factura sin modificar en caso de error
        return {'factura': factura}