import os
import pyodbc
import logging
from typing import Optional, Dict, Any
from dotenv import load_dotenv
from contextlib import contextmanager
from pathlib import Path

# Cargar variables de entorno desde la raíz del proyecto
env_path = Path(__file__).parent.parent.parent / '.env'
#print(f"📂 Cargando .env desde: {env_path}")  # Para verificar
load_dotenv(dotenv_path=env_path)

logger = logging.getLogger(__name__)


class DatabaseConfig:
    """
    Configuración centralizada de base de datos usando variables de entorno.
    Basado en la conexión exitosa con Driver 17.
    """
    
    _instance = None
    _connection_string = None
    
    def __new__(cls):
        """Patrón Singleton para asegurar una sola instancia de configuración"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load_config()
        return cls._instance
    
    def _load_config(self):
        """Carga la configuración desde variables de entorno"""
        # Obtener valores con validación
        self.driver = self._get_required('DB_DRIVER')
        self.server_ip = self._get_required('DB_SERVER')
        self.port = self._get_int('DB_PORT', 1433)
        self.database = self._get_required('DB_NAME')
        self.username = self._get_required('DB_USER')
        self.password = self._get_required('DB_PASSWORD')
        self.timeout = self._get_int('DB_TIMEOUT', 30)
        self.encrypt = self._get_encrypt_value('DB_ENCRYPT', 'yes')
        self.trust_cert = self._get_trust_value('DB_TRUST_SERVER_CERTIFICATE', 'yes')
        
        # Construir server con puerto (como en tu script exitoso)
        if self.port != 1433:
            self.server = f"{self.server_ip},{self.port}"
        else:
            self.server = self.server_ip
        
        # Construir connection string
        self._build_connection_string()
    
    def _get_required(self, key: str) -> str:
        """Obtiene variable requerida o lanza error"""
        value = os.getenv(key)
        if not value:
            raise ValueError(f"Variable de entorno requerida '{key}' no está configurada")
        return value
    
    def _get_int(self, key: str, default: int) -> int:
        """Obtiene variable como entero"""
        value = os.getenv(key)
        if not value:
            return default
        try:
            return int(value)
        except ValueError:
            logger.warning(f"Valor inválido para {key}, usando default {default}")
            return default
    
    def _get_encrypt_value(self, key: str, default: str) -> str:
        """Obtiene valor de encrypt (puede ser 'yes'/'no' o 'true'/'false')"""
        value = os.getenv(key, default).lower()
        if value in ('yes', 'true', '1', 'on'):
            return 'yes'
        return 'no'
    
    def _get_trust_value(self, key: str, default: str) -> str:
        """Obtiene valor de trust certificate"""
        value = os.getenv(key, default).lower()
        if value in ('yes', 'true', '1', 'on'):
            return 'yes'
        return 'no'
    
    def _build_connection_string(self):
        """Construye el connection string para pyodbc (igual que tu script exitoso)"""
        self._connection_string = (
            f"DRIVER={self.driver};"
            f"SERVER={self.server};"
            f"DATABASE={self.database};"
            f"UID={self.username};"
            f"PWD={self.password};"
        )
        #logger.debug("Connection string construido (credenciales ocultas)")
    
    def get_connection_string_masked(self) -> str:
        """Versión segura del connection string para logging"""
        masked = self._connection_string.replace(self.password, '********')
        return masked
    
    def __repr__(self) -> str:
        """Representación segura de la configuración"""
        return (
            f"DatabaseConfig(server={self.server}, "
            f"database={self.database}, "
            f"user={self.username}, "
            f"timeout={self.timeout})"
        )


class DatabaseConnection:
    """
    Manejador de conexiones a base de datos con pyodbc.
    Adaptado de tu script exitoso.
    """
    
    def __init__(self):
        self.config = DatabaseConfig()
        self._connection = None
        self._listar_drivers_disponibles()
    
    def _listar_drivers_disponibles(self):
        """Lista los drivers disponibles (útil para debugging)"""
        try:
            drivers = pyodbc.drivers()
            #logger.debug(f"🔧 Drivers ODBC disponibles: {drivers}")
        except Exception as e:
            logger.warning(f"No se pudieron listar drivers: {e}")
    
    def connect(self) -> pyodbc.Connection:
        """
        Establece conexión con la base de datos.
        Implementa la misma lógica que tu script exitoso.
        """
        try:
            if self._connection is None or self._connection.closed:
                logger.info(f"Conectando a {self.config.server}/{self.config.database}")
                logger.debug(f"Usando driver: {self.config.driver}")
                
                # Exactamente la misma cadena que funcionó en tu script
                conn_str = self.config._connection_string
                
                self._connection = pyodbc.connect(conn_str, timeout=self.config.timeout)
                logger.info("✅ Conexión exitosa")
            return self._connection
        except pyodbc.Error as e:
            logger.error(f"❌ Error de conexión: {str(e)}")
            logger.error(f"Driver usado: {self.config.driver}")
            logger.error(f"Servidor: {self.config.server}")
            raise ConnectionError(f"No se pudo conectar a la base de datos: {str(e)}")
    
    def close(self):
        """Cierra la conexión si está abierta"""
        if self._connection and not self._connection.closed:
            self._connection.close()
            logger.info("🔒 Conexión cerrada")
    
    @contextmanager
    def transaction(self):
        """
        Context manager para manejar transacciones automáticamente.
        """
        conn = self.connect()
        cursor = conn.cursor()
        try:
            yield cursor
            conn.commit()
            logger.debug("Transacción confirmada")
        except Exception as e:
            conn.rollback()
            logger.error(f"Error en transacción, rollback ejecutado: {str(e)}")
            raise
        finally:
            cursor.close()
    
    def execute_query(self, query: str, params: tuple = (), fetch: bool = False):
        """
        Ejecuta una consulta SQL con parámetros.
        """
        with self.transaction() as cursor:
            logger.debug(f"Ejecutando query: {query[:100]}...")
            cursor.execute(query, params)
            
            if fetch:
                columns = [column[0] for column in cursor.description]
                results = []
                for row in cursor.fetchall():
                    results.append(dict(zip(columns, row)))
                return results
            return None
    
    def __enter__(self):
        """Soporte para context manager"""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Cierra conexión al salir del context manager"""
        self.close()


# Instancia global para reutilizar
db = DatabaseConnection()