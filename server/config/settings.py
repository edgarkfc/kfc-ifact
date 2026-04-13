# server/config/settings.py
"""
Configuraciones centralizadas del proyecto
"""
import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent.parent

class Config:
    """Configuración base"""
    # Flask
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-key-change-in-production')
    DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'
    
    # Database (SQLAlchemy)
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL',
        f'sqlite:///{BASE_DIR}/instance/app.db'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = DEBUG
    
    # Configuración de facturación
    LINEA_FINAL_FACTURA = "199\n"
    LINEA_FINAL_NOTA_CREDITO = "199\n"
    
    # Configuración de impresión
    IMPRESORA_POR_DEFECTO = os.getenv('IMPRESORA', 'thermal')
    TIMEOUT_IMPRESION = int(os.getenv('TIMEOUT_IMPRESION', 30))
    IMPRIMIR_QR_POR_DEFECTO = os.getenv('IMPRIMIR_QR', 'False').lower() == 'true'
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', 'logs/app.log')
    
    # API
    API_VERSION = "2.0.0"
    API_PREFIX = "/api"

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_ECHO = True

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    DEBUG = False

class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_ECHO = False

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}