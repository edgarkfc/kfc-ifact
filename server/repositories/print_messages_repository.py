# database/print_messages_repository.py
import logging
from typing import Dict, Any, List, Optional

from server.config.database import db

logger = logging.getLogger(__name__)


class PrintMessagesRepository:
    """
    Repositorio para manejar la tabla print_messages
    """
    
    def __init__(self):
        """Inicializa el repositorio usando la conexión global"""
        self.db = db
    
    def get_all_active_ordered(self) -> List[Dict[str, Any]]:
        """
        Obtiene todos los mensajes activos ordenados
        
        Returns:
            Lista de diccionarios con los mensajes activos ordenados
        """
        try:
            query = """
                SELECT [id], [code], [content], [is_active], [order]
                FROM [iFact].[dbo].[print_messages]
                WHERE [is_active] = 1
                ORDER BY [order] ASC
            """
            
            results = self.db.execute_query(query, fetch=True)
            
            if results:
                logger.debug(f"Se obtuvieron {len(results)} mensajes activos")
                return results
            else:
                logger.info("No se encontraron mensajes activos en print_messages")
                return []
                
        except Exception as e:
            logger.error(f"Error al obtener mensajes activos: {e}")
            return []
    
    def get_message_lines(self) -> List[str]:
        """
        Obtiene las líneas de mensaje formateadas para la impresora fiscal
        
        Returns:
            Lista de strings con el formato 'code content\\n'
        """
        try:
            messages = self.get_all_active_ordered()
            lines = []
            
            for message in messages:
                # Formato para la impresora fiscal: código + espacio + contenido + salto de línea
                line = f"{message.get('code', '')} {message.get('content', '')}\n"
                lines.append(line)
            
            logger.debug(f"Se generaron {len(lines)} líneas de mensaje")
            return lines
            
        except Exception as e:
            logger.error(f"Error al generar líneas de mensaje: {e}")
            return []
    
    def get_message_by_id(self, message_id: int) -> Optional[Dict[str, Any]]:
        """
        Obtiene un mensaje específico por su ID
        
        Args:
            message_id: ID del mensaje
        
        Returns:
            Diccionario con los datos del mensaje o None si no existe
        """
        try:
            query = """
                SELECT [id], [code], [content], [is_active], [order]
                FROM [iFact].[dbo].[print_messages]
                WHERE [id] = ?
            """
            params = (message_id,)
            
            results = self.db.execute_query(query, params, fetch=True)
            
            if results and len(results) > 0:
                logger.debug(f"Mensaje obtenido: {results[0]}")
                return results[0]
            else:
                logger.warning(f"No se encontró mensaje con ID={message_id}")
                return None
                
        except Exception as e:
            logger.error(f"Error al obtener mensaje por ID {message_id}: {e}")
            return None
    
    def get_active_messages_count(self) -> int:
        """
        Obtiene el número de mensajes activos
        
        Returns:
            int: Número de mensajes activos
        """
        try:
            query = """
                SELECT COUNT(*) as total
                FROM [iFact].[dbo].[print_messages]
                WHERE [is_active] = 1
            """
            
            results = self.db.execute_query(query, fetch=True)
            
            if results and len(results) > 0:
                return results[0].get('total', 0)
            return 0
                
        except Exception as e:
            logger.error(f"Error al contar mensajes activos: {e}")
            return 0
    
    def insert_message(self, code: str, content: str, is_active: int = 1, order: int = 0) -> bool:
        """
        Inserta un nuevo mensaje en la tabla print_messages
        
        Args:
            code: Código del mensaje
            content: Contenido del mensaje
            is_active: Estado (1 para activo, 0 para inactivo)
            order: Orden de impresión
        
        Returns:
            bool: True si se insertó correctamente
        """
        try:
            query = """
                INSERT INTO [iFact].[dbo].[print_messages] 
                ([code], [content], [is_active], [order])
                VALUES (?, ?, ?, ?)
            """
            params = (code, content, is_active, order)
            
            self.db.execute_query(query, params)
            logger.info(f"Mensaje insertado: code={code}, content={content}")
            return True
            
        except Exception as e:
            logger.error(f"Error al insertar mensaje: {e}")
            return False
    
    def update_message(self, message_id: int, **kwargs) -> bool:
        """
        Actualiza un mensaje existente
        
        Args:
            message_id: ID del mensaje a actualizar
            **kwargs: Campos a actualizar (code, content, is_active, order)
        
        Returns:
            bool: True si se actualizó correctamente
        """
        try:
            # Construir dinámicamente la consulta de actualización
            set_clause = []
            params = []
            
            allowed_fields = ['code', 'content', 'is_active', 'order']
            
            for field in allowed_fields:
                if field in kwargs and kwargs[field] is not None:
                    set_clause.append(f"[{field}] = ?")
                    params.append(kwargs[field])
            
            if not set_clause:
                logger.warning("No se proporcionaron campos para actualizar")
                return False
            
            # Agregar el ID al final de los parámetros
            params.append(message_id)
            
            query = f"""
                UPDATE [iFact].[dbo].[print_messages]
                SET {', '.join(set_clause)}
                WHERE [id] = ?
            """
            
            self.db.execute_query(query, tuple(params))
            logger.info(f"Mensaje actualizado para ID={message_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error al actualizar mensaje: {e}")
            return False
    
    def delete_message(self, message_id: int) -> bool:
        """
        Elimina un mensaje de la tabla print_messages
        
        Args:
            message_id: ID del mensaje a eliminar
        
        Returns:
            bool: True si se eliminó correctamente
        """
        try:
            query = """
                DELETE FROM [iFact].[dbo].[print_messages]
                WHERE [id] = ?
            """
            params = (message_id,)
            
            self.db.execute_query(query, params)
            logger.info(f"Mensaje eliminado con ID={message_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error al eliminar mensaje con ID {message_id}: {e}")
            return False
    
    def set_message_status(self, message_id: int, is_active: int) -> bool:
        """
        Cambia el estado de un mensaje
        
        Args:
            message_id: ID del mensaje
            is_active: Nuevo estado (1 para activo, 0 para inactivo)
        
        Returns:
            bool: True si se actualizó correctamente
        """
        return self.update_message(message_id, is_active=is_active)
    
    def reorder_messages(self, message_ids: List[int]) -> bool:
        """
        Reordena los mensajes según la lista de IDs proporcionada
        
        Args:
            message_ids: Lista de IDs en el orden deseado
        
        Returns:
            bool: True si se reordenaron correctamente
        """
        try:
            # Actualizar el orden de cada mensaje
            for index, message_id in enumerate(message_ids):
                success = self.update_message(message_id, order=index)
                if not success:
                    logger.error(f"Error al actualizar orden para mensaje ID={message_id}")
                    return False
            
            logger.info(f"Mensajes reordenados correctamente")
            return True
            
        except Exception as e:
            logger.error(f"Error al reordenar mensajes: {e}")
            return False