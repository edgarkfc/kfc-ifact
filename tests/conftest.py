# tests/conftest.py
import sys
import os
import pytest

# Agregar la ruta del proyecto al Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)


from server.routes.api import facturas_bp
import json

@pytest.fixture
def app():
    """Fixture para crear la aplicación Flask para testing"""
    from flask import Flask
    app = Flask(__name__)
    app.register_blueprint(facturas_bp)
    app.config['TESTING'] = True
    return app

@pytest.fixture
def client(app):
    """Fixture para el cliente de pruebas"""
    return app.test_client()

@pytest.fixture
def runner(app):
    """CLI runner para pruebas"""
    return app.test_cli_runner()

@pytest.fixture
def validar_factura():
    """Fixture con datos de factura válidos"""
    return {
        "factura": {
            "cliente": {
                "cli_documento": "12345678",
                "cli_nombres": "Juan Pérez García",
                "cli_telefono": "77712345",
                "cli_direccion": "Av. Siempre Viva #123"
            },
            "detalle_factura": [
                {
                    "producto": "Producto 1",
                    "cantidad": 2,
                    "precio": 100.50
                },
                {
                    "producto": "Producto 2",
                    "cantidad": 1,
                    "precio": 50.25
                }
            ],
            "formas_pago": [
                {
                    "IDFormapago": 1,
                    "fpf_total_pagar": 201.00,
                    "Formapago_FacturaVarchar4": "01"
                }
            ]
        }
    }

@pytest.fixture
def factura_sin_cliente():
    """Fixture con factura sin datos de cliente"""
    return {
        "factura": {
            "detalle_factura": [
                {
                    "producto": "Producto 1",
                    "cantidad": 2,
                    "precio": 100.50
                }
            ],
            "formas_pago": [
                {
                    "fpf_total_pagar": 201.00,
                    "Formapago_FacturaVarchar4": "01"
                }
            ]
        }
    }

@pytest.fixture
def factura_cliente_incompleto():
    """Fixture con cliente con campos incompletos"""
    return {
        "factura": {
            "cliente": {
                "cli_documento": "12345678",
                "cli_nombres": "",
                "cli_telefono": None,
                "cli_direccion": "   "
            },
            "detalle_factura": [
                {
                    "producto": "Producto 1",
                    "cantidad": 2,
                    "precio": 100.50
                }
            ],
            "formas_pago": [
                {
                    "fpf_total_pagar": 201.00,
                    "Formapago_FacturaVarchar4": "01"
                }
            ]
        }
    }

@pytest.fixture
def factura_forma_pago_invalida():
    """Fixture con forma de pago inválida"""
    return {
        "factura": {
            "cliente": {
                "cli_documento": "12345678",
                "cli_nombres": "Juan Pérez",
                "cli_telefono": "77712345",
                "cli_direccion": "Av. Siempre Viva"
            },
            "detalle_factura": [
                {
                    "producto": "Producto 1",
                    "cantidad": 2,
                    "precio": 100.50
                }
            ],
            "formas_pago": [
                {
                    "fpf_total_pagar": -100.00,
                    "Formapago_FacturaVarchar4": "999"
                }
            ]
        }
    }