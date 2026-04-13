# server/repositories/print_messages_repository.py
"""
Repositorio para mensajes de impresión - Versión PyODBC
"""
import logging
from typing import List, Dict, Any
from server.config.database import db

logger = logging.getLogger(__name__)


class PrintMessagesRepository:
    """Repositorio para gestionar mensajes de impresión"""
    
    def get_all_active_ordered(self) -> List[Dict[str, Any]]:
        """Obtiene todos los mensajes activos ordenados"""
        try:
            query = """
                SELECT id, code, content, [order], is_active, created_at, updated_at
                FROM print_messages
                WHERE is_active = 1
                ORDER BY [order] ASC
            """
            results = db.execute_query(query, fetch=True)
            return results if results else []
        except Exception as e:
            logger.error(f"Error obteniendo mensajes activos: {e}")
            return []
    
    def get_by_code(self, code: str) -> Dict[str, Any]:
        """Obtiene un mensaje por código"""
        try:
            query = """
                SELECT id, code, content, [order], is_active
                FROM print_messages
                WHERE code = ? AND is_active = 1
            """
            results = db.execute_query(query, (code,), fetch=True)
            return results[0] if results else None
        except Exception as e:
            logger.error(f"Error obteniendo mensaje por código {code}: {e}")
            return None
    
    def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Crea un nuevo mensaje"""
        try:
            query = """
                INSERT INTO print_messages (code, content, [order], is_active, created_at, updated_at)
                VALUES (?, ?, ?, ?, GETDATE(), GETDATE());
                SELECT SCOPE_IDENTITY() as id;
            """
            params = (
                data.get('code'),
                data.get('content'),
                data.get('order', 0),
                1 if data.get('is_active', True) else 0
            )
            result = db.execute_query(query, params, fetch=True)
            if result:
                data['id'] = result[0]['id']
            return data
        except Exception as e:
            logger.error(f"Error creando mensaje: {e}")
            raise
    
    def update(self, msg_id: int, data: Dict[str, Any]) -> bool:
        """Actualiza un mensaje existente"""
        try:
            updates = []
            params = []
            
            if 'code' in data:
                updates.append("code = ?")
                params.append(data['code'])
            if 'content' in data:
                updates.append("content = ?")
                params.append(data['content'])
            if 'order' in data:
                updates.append("[order] = ?")
                params.append(data['order'])
            if 'is_active' in data:
                updates.append("is_active = ?")
                params.append(1 if data['is_active'] else 0)
            
            if not updates:
                return True
            
            updates.append("updated_at = GETDATE()")
            params.append(msg_id)
            
            query = f"UPDATE print_messages SET {', '.join(updates)} WHERE id = ?"
            db.execute_query(query, tuple(params))
            return True
        except Exception as e:
            logger.error(f"Error actualizando mensaje {msg_id}: {e}")
            return False
    
    def delete(self, msg_id: int) -> bool:
        """Elimina un mensaje (soft delete)"""
        try:
            query = "UPDATE print_messages SET is_active = 0, updated_at = GETDATE() WHERE id = ?"
            db.execute_query(query, (msg_id,))
            return True
        except Exception as e:
            logger.error(f"Error eliminando mensaje {msg_id}: {e}")
            return False