# database/pivotqrs_repository.py
import logging
from typing import Dict, Any, List, Optional
from server.config.database import db

logger = logging.getLogger(__name__)


class PivotQRSRepository:
    """
    Repositorio para manejar la tabla pivotqrs
    """
    
    # Valores por defecto en caso de error o sin datos
    DEFAULT_VALUES = {
        'id': None,
        'nropases': 0,
        'nrotarjetas': 0,
        'hora': 0,
        'minutos': 0,
        'status': 'INACTIVO'
    }
    
    def __init__(self):
        """Inicializa el repositorio usando la conexión global"""
        self.db = db
    
    def get_parametros_qr(self, id_parametro: Optional[int] = None) -> Dict[str, Any]:
        """
        Obtiene los parámetros de la tabla pivotqrs
        
        Args:
            id_parametro: ID específico del parámetro (opcional)
        
        Returns:
            Dict con los parámetros o valores por defecto
        """
        try:
            # Construir la consulta
            if id_parametro:
                query = """
                    SELECT TOP (1) [id], [nropases], [nrotarjetas], [hora], [minutos], [status]
                    FROM [iFact].[dbo].[pivotqrs]
                    WHERE [id] = ?
                    ORDER BY [id] DESC
                """
                params = (id_parametro,)
            else:
                query = """
                    SELECT TOP (1) [id], [nropases], [nrotarjetas], [hora], [minutos], [status]
                    FROM [iFact].[dbo].[pivotqrs]
                    ORDER BY [id] DESC
                """
                params = ()
            
            # Ejecutar consulta usando tu método execute_query
            results = self.db.execute_query(query, params, fetch=True)
            
            # Si hay datos, retornarlos
            if results and len(results) > 0:
                row = results[0]
                logger.debug(f"Parámetros QR obtenidos: {row}")
                return {
                    'id': row.get('id'),
                    'nropases': row.get('nropases', 0),
                    'nrotarjetas': row.get('nrotarjetas', 0),
                    'hora': row.get('hora', 0),
                    'minutos': row.get('minutos', 0),
                    'status': row.get('status', 'INACTIVO')
                }
            else:
                logger.warning("No se encontraron parámetros en pivotqrs, usando valores por defecto")
                return self.DEFAULT_VALUES.copy()
                
        except Exception as e:
            logger.error(f"Error al obtener parámetros QR: {e}")
            return self.DEFAULT_VALUES.copy()
    
    def get_parametros_qr_list(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Obtiene una lista de parámetros de la tabla pivotqrs
        
        Args:
            limit: Número máximo de registros a obtener
        
        Returns:
            Lista de diccionarios con los parámetros
        """
        try:
            query = f"""
                SELECT TOP ({limit}) [id], [nropases], [nrotarjetas], [hora], [minutos], [status]
                FROM [iFact].[dbo].[pivotqrs]
                ORDER BY [id] DESC
            """
            
            results = self.db.execute_query(query, fetch=True)
            
            if results:
                logger.debug(f"Se obtuvieron {len(results)} registros de pivotqrs")
                return results
            else:
                logger.warning("No se encontraron parámetros en pivotqrs")
                return []
                
        except Exception as e:
            logger.error(f"Error al obtener lista de parámetros QR: {e}")
            return []
    
    def get_parametro_especifico(self, campo: str, id_parametro: Optional[int] = None) -> Any:
        """
        Obtiene un campo específico de los parámetros
        
        Args:
            campo: Nombre del campo a obtener ('nropases', 'nrotarjetas', 'hora', 'minutos', 'status')
            id_parametro: ID específico del parámetro (opcional)
        
        Returns:
            Valor del campo o valor por defecto según el tipo
        """
        parametros = self.get_parametros_qr(id_parametro)
        
        if campo in parametros:
            return parametros[campo]
        else:
            logger.warning(f"Campo {campo} no encontrado, usando valor por defecto")
            return self.DEFAULT_VALUES.get(campo, None)
    
    def get_nropases(self, id_parametro: Optional[int] = None) -> int:
        """Obtiene solo el número de pases"""
        return self.get_parametro_especifico('nropases', id_parametro)
    
    def get_nrotarjetas(self, id_parametro: Optional[int] = None) -> int:
        """Obtiene solo el número de tarjetas"""
        return self.get_parametro_especifico('nrotarjetas', id_parametro)
    
    def get_tiempo_qr(self, id_parametro: Optional[int] = None) -> tuple:
        """
        Obtiene el tiempo de espera para QR
        
        Returns:
            tuple: (hora, minutos)
        """
        parametros = self.get_parametros_qr(id_parametro)
        return parametros.get('hora', 0), parametros.get('minutos', 0)
    
    def get_status(self, id_parametro: Optional[int] = None) -> str:
        """Obtiene el status"""
        return self.get_parametro_especifico('status', id_parametro)
    
    def insert_parametros(self, nropases: int, nrotarjetas: int, hora: int, minutos: int, status: str = 'ACTIVO') -> bool:
        """
        Inserta nuevos parámetros en la tabla pivotqrs
        
        Args:
            nropases: Número de pases
            nrotarjetas: Número de tarjetas
            hora: Horas de espera
            minutos: Minutos de espera
            status: Estado ('ACTIVO' o 'INACTIVO')
        
        Returns:
            bool: True si se insertó correctamente
        """
        try:
            query = """
                INSERT INTO [iFact].[dbo].[pivotqrs] 
                ([nropases], [nrotarjetas], [hora], [minutos], [status])
                VALUES (?, ?, ?, ?, ?)
            """
            params = (nropases, nrotarjetas, hora, minutos, status)
            
            self.db.execute_query(query, params)
            logger.info(f"Parámetros QR insertados: pases={nropases}, tarjetas={nrotarjetas}")
            return True
            
        except Exception as e:
            logger.error(f"Error al insertar parámetros QR: {e}")
            return False
    
    def update_parametros(self, id_parametro: int, **kwargs) -> bool:
        """
        Actualiza parámetros existentes
        
        Args:
            id_parametro: ID del registro a actualizar
            **kwargs: Campos a actualizar (nropases, nrotarjetas, hora, minutos, status)
        
        Returns:
            bool: True si se actualizó correctamente
        """
        try:
            # Construir dinámicamente la consulta de actualización
            set_clause = []
            params = []
            
            allowed_fields = ['nropases', 'nrotarjetas', 'hora', 'minutos', 'status']
            
            for field in allowed_fields:
                if field in kwargs and kwargs[field] is not None:
                    set_clause.append(f"[{field}] = ?")
                    params.append(kwargs[field])
            
            if not set_clause:
                logger.warning("No se proporcionaron campos para actualizar")
                return False
            
            # Agregar el ID al final de los parámetros
            params.append(id_parametro)
            
            query = f"""
                UPDATE [iFact].[dbo].[pivotqrs]
                SET {', '.join(set_clause)}
                WHERE [id] = ?
            """
            
            self.db.execute_query(query, tuple(params))
            logger.info(f"Parámetros QR actualizados para ID={id_parametro}")
            return True
            
        except Exception as e:
            logger.error(f"Error al actualizar parámetros QR: {e}")
            return False
