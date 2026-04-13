# server/__init__.py
"""
Server package - Configuración principal
Sin SQLAlchemy, solo Flask
"""
from flask import Flask
import logging
import os

logger = logging.getLogger(__name__)


def create_app(config_name='default'):
    """Application factory pattern"""
    app = Flask(__name__)
    
    # Configuraciones básicas
    app.config['JSON_SORT_KEYS'] = False
    app.config['JSON_AS_ASCII'] = False
    
    # Registrar rutas
    from server.routes import register_routes
    register_routes(app)
    
    logger.info("✅ Aplicación creada exitosamente")
    return app