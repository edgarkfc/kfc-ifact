# app.py - Versión final sin SQLAlchemy
from flask import Flask
import logging
import sys
import os

# Agregar el directorio padre al path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Importar rutas originales
from server.routes.api import facturas_bp, notas_credito_bp

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def create_app():
    """Factory function para crear la aplicación Flask"""
    app = Flask(__name__)
    
    # Configuraciones
    app.config['JSON_SORT_KEYS'] = False
    app.config['JSON_AS_ASCII'] = False
    
    # Registrar blueprints originales
    app.register_blueprint(facturas_bp)
    app.register_blueprint(notas_credito_bp)
    
    # NOTA: Rutas /health y /health/db ELIMINADAS
    
    logger.info("✅ Aplicación Flask creada exitosamente")
    return app


if __name__ == '__main__':
    app = create_app()
    
    # Configuración desde variables de entorno
    debug = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    host = os.getenv('FLASK_HOST', '0.0.0.0')
    port = int(os.getenv('FLASK_PORT', 5000))
    
    logger.info(f"🚀 Iniciando servidor en {host}:{port} (debug={debug})")
    app.run(debug=debug, host=host, port=port)