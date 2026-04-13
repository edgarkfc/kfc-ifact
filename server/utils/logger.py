# server/utils/logger.py
"""
Configuración centralizada de logging
"""
import logging
import sys
from pathlib import Path
from server.config.settings import Config

def setup_logger(name: str = None, log_file: str = None) -> logging.Logger:
    """Configura y retorna un logger"""
    logger = logging.getLogger(name or __name__)
    
    if not logger.handlers:
        log_level = getattr(logging, Config.LOG_LEVEL.upper())
        logger.setLevel(log_level)
        
        # Formato
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
        )
        
        # Handler para consola
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(log_level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        # Handler para archivo (si está configurado)
        log_path = log_file or Config.LOG_FILE
        if log_path:
            try:
                # Crear directorio de logs si no existe
                Path(log_path).parent.mkdir(parents=True, exist_ok=True)
                
                file_handler = logging.FileHandler(log_path, encoding='utf-8')
                file_handler.setLevel(logging.INFO)
                file_handler.setFormatter(formatter)
                logger.addHandler(file_handler)
            except Exception as e:
                logger.warning(f"No se pudo crear archivo de log: {e}")
    
    return logger

# Logger por defecto
default_logger = setup_logger('server')

# Logger para cada módulo
def get_logger(name: str):
    """Obtiene un logger configurado para un módulo específico"""
    return setup_logger(f'server.{name}')