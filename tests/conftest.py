import sys
import os
import pytest
import json
from flask import Flask
from flask.testing import FlaskClient

# Agregar la raíz del proyecto al path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Importar correctamente desde server/routes/api
from server.routes.api import facturas_bp
from datetime import datetime

@pytest.fixture
def app():
    """Fixture para crear la aplicación Flask para pruebas"""
    app = Flask(__name__)
    app.register_blueprint(facturas_bp)
    app.config['TESTING'] = True
    app.config['DEBUG'] = False
    
    # Configuración adicional para pruebas
    app.config['SERVER_NAME'] = 'localhost'
    
    ctx = app.app_context()
    ctx.push()
    
    yield app
    
    ctx.pop()

@pytest.fixture
def client(app: Flask) -> FlaskClient:
    """Fixture para el cliente de pruebas"""
    return app.test_client()

@pytest.fixture
def factura_valida_data():
    """Fixture con datos de factura válida"""
    from tests.fixtures.factura_data import FACTURA_VALIDA
    return FACTURA_VALIDA

@pytest.fixture
def factura_valida_multiple_data():
    """Fixture con datos de factura válida con múltiples productos"""
    from tests.fixtures.factura_data import FACTURA_VALIDA_MULTIPLE
    return FACTURA_VALIDA_MULTIPLE

@pytest.fixture
def factura_invalida_data():
    """Fixture con datos de factura inválida"""
    from tests.fixtures.factura_data import FACTURA_INVALIDA
    return FACTURA_INVALIDA

@pytest.fixture
def factura_diferencia_totales_data():
    """Fixture con factura que tiene diferencia en totales"""
    from tests.fixtures.factura_data import FACTURA_DIFERENCIA_TOTALES
    return FACTURA_DIFERENCIA_TOTALES

@pytest.fixture
def mock_print_message(monkeypatch):
    """Mock para print_message"""
    def mock_print(*args, **kwargs):
        return {'factura': ['línea1', 'línea2']}
    
    # Mockear la función print_message
    monkeypatch.setattr('server.controllers.bills_controller.print_message', mock_print)
    return mock_print

@pytest.fixture
def mock_cabeceraFacturas(monkeypatch):
    """Mock para cabeceraFacturas para evitar conexión a DB"""
    def mock_cabecera(*args, **kwargs):
        return ['línea cabecera 1', 'línea cabecera 2']
    
    monkeypatch.setattr('server.controllers.bills_controller.cabeceraFacturas', mock_cabecera)
    return mock_cabecera

@pytest.fixture
def mock_factura_productos(monkeypatch):
    """Mock para factura_productos para evitar conexión a DB"""
    def mock_productos(*args, **kwargs):
        return {'factura': ['producto 1', 'producto 2'], 'detalle': []}
    
    monkeypatch.setattr('server.controllers.bills_controller.factura_productos', mock_productos)
    return mock_productos

@pytest.fixture
def mock_factura_pagos(monkeypatch):
    """Mock para factura_pagos para evitar conexión a DB"""
    def mock_pagos(*args, **kwargs):
        return ['pago 1', 'pago 2']
    
    monkeypatch.setattr('server.controllers.bills_controller.factura_pagos', mock_pagos)
    return mock_pagos

@pytest.fixture
def mock_validar_mensaje_qr(monkeypatch):
    """Mock para validar_mensaje_qr"""
    def mock_validar_qr(*args, **kwargs):
        return False
    
    monkeypatch.setattr('server.controllers.bills_controller.validar_mensaje_qr', mock_validar_qr)
    return mock_validar_qr