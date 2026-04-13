# server/repositories/pivotqrs_repository.py

import logging
from typing import Dict, Any, Optional, List
from server.config.database import db

logger = logging.getLogger(__name__)


class PivotQRSRepository:
    """Repositorio para parámetros de QR"""
    
    # Nombre correcto de la tabla
    TABLE_NAME = "pivotqrs"  # Ajusta según tu tabla real
    
    def get_parametros_qr(self) -> Optional[Dict[str, Any]]:
        """Obtiene los parámetros activos para generación de QR"""
        try:
            # Si status es bit, usar 1 en lugar de 'ACTIVO'
            query = f"""
                SELECT TOP 1 
                    id, 
                    nropases, 
                    nrotarjetas, 
                    hora, 
                    minutos, 
                    status
                FROM {self.TABLE_NAME}
                WHERE status = 1  -- 1 = activo, 0 = inactivo
                ORDER BY id DESC
            """
            results = db.execute_query(query, fetch=True)
            
            if results:
                return results[0]
            else:
                logger.warning("No se encontraron parámetros QR activos")
                return None
                
        except Exception as e:
            logger.error(f"Error obteniendo parámetros QR: {e}")
            return None
    
    def update_parametros(self, id_parametro: int, **kwargs) -> bool:
        """Actualiza parámetros QR en la base de datos"""
        try:
            updates = []
            params = []
            
            for key, value in kwargs.items():
                updates.append(f"{key} = ?")
                params.append(value)
            
            if not updates:
                return True
            
            params.append(id_parametro)
            query = f"UPDATE {self.TABLE_NAME} SET {', '.join(updates)} WHERE id = ?"
            db.execute_query(query, tuple(params))
            return True
            
        except Exception as e:
            logger.error(f"Error actualizando parámetros QR: {e}")
            return False
    
    def get_all_active(self) -> List[Dict[str, Any]]:
        """Obtiene todos los parámetros activos"""
        try:
            query = f"""
                SELECT id, nropases, nrotarjetas, hora, minutos, status
                FROM {self.TABLE_NAME}
                WHERE status = 1  -- 1 = activo, 0 = inactivo
                ORDER BY id ASC
            """
            results = db.execute_query(query, fetch=True)
            return results if results else []
        except Exception as e:
            logger.error(f"Error obteniendo todos los parámetros: {e}")
            return []