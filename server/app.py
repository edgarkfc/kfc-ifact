# app.py
from flask import Flask
import logging
import sys
import os

# Agregar el directorio padre al path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from server.routes.api import facturas_bp
# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def create_app():
    """Factory function para crear la aplicación Flask"""
    app = Flask(__name__)
    
    # Configuraciones
    app.config['JSON_SORT_KEYS'] = False  # Mantener orden de keys
    app.config['JSON_AS_ASCII'] = False   # Permitir caracteres UTF-8
    
    # Registrar blueprints
    app.register_blueprint(facturas_bp)
    # Puedes registrar más blueprints aquí
    # app.register_bluespace(otro_bp)
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)