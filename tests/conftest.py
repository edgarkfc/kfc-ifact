# tests/conftest.py
"""
Configuración global de pytest y fixtures reutilizables
"""
import sys
import os
import pytest
import json
from pathlib import Path

from sqlalchemy import Null

# Agregar el directorio del proyecto al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from server.app import create_app
from server.config.database import db as database_db


@pytest.fixture
def app():
    """Fixture para la aplicación Flask"""
    app = create_app()
    app.config['TESTING'] = True
    app.config['SERVER_NAME'] = 'localhost.localdomain'
    
    with app.app_context():
        yield app


@pytest.fixture
def client(app):
    """Fixture para el cliente de pruebas"""
    return app.test_client()


@pytest.fixture
def db_connection():
    """Fixture para conexión a base de datos de prueba"""
    # Aquí puedes configurar una BD de prueba si es necesario
    yield database_db


@pytest.fixture
def factura_valida():
    """Fixture con datos de factura válida (con fecha)"""
    return {
        "factura": {
            "restaurante": {
            "restaurante": "K098",
            "rest_id": 45,
            "impuesto_rest": True,
            "nro_estacion": 1
            },
            "config_impresora": {
            "impresion_qr": True,
            "impresion_msgqr": True,
            "impresion_cupon": False
            },
            "cabecera_factura": {
            "cabfact_id": "K098F000000576",
            "cabfact_nrofact_nc": "0000",
            "delivery_id": "PEYA-1921213682",
            "cabfact_fechacreacion": "2026-02-26T16:29:57.133",
            "cabfact_subtotal": 4183.1724,
            "cabfact_iva": 669.31,
            "cabfact_total": 4852.48,
            "cabfact_valor_descuento": 0,
            "cabfact_porcentaje_descuento": 0,
            "cabfact_cajero": "lgarcia",
            "cabfact_tasa_conversion": 414.04
            },
            "detalle_factura": [
            {
                "detallefactura_id": "8DBF8DE7-5113-F111-ADF8-D0C1B5009507",
                "dtfacplu_id": 4178,
                "dtfac_cantidad": 2,
                "dtfac_precio_unitario": 2426.24,
                "dtfac_iva": 334.65,
                "dtfac_total": 4852.48,
                "aplicaImpuesto1": 1,
                "aplicaImpuesto2": 0,
                "aplicaImpuesto3": 0,
                "aplicaImpuesto4": 0,
                "aplicaImpuesto5": 0,
                "dtfac_valor_descuento": 0,
                "dtfac_porcentaje_descuento": 0,
                "dtfac_totaldesc":0,
                "dtfac_ivadesc": 0,
                "dtfac_descripcion": "COMBO 2PZ CON PAPAS"
            },
            {
                "detallefactura_id": "8CBF8DE7-5113-F111-ADF8-D0C1B5009507",        
                "dtfacplu_id": 258,
                "dtfac_cantidad": 1,
                "dtfac_precio_unitario": 0,
                "dtfac_iva": 0,
                "dtfac_total": 0,
                "aplicaImpuesto1": 1,
                "aplicaImpuesto2": 0,
                "aplicaImpuesto3": 0,
                "aplicaImpuesto4": 0,
                "aplicaImpuesto5": 0,
                "dtfac_valor_descuento": 0,
                "dtfac_porcentaje_descuento": 0,
                "dtfac_totaldesc": 0,
                "dtfac_ivadesc": 0,
                "dtfac_descripcion": ".No"        
            },
            {
                "detallefactura_id": "8BBF8DE7-5113-F111-ADF8-D0C1B5009507",       
                "dtfacplu_id": 246,
                "dtfac_cantidad": 1,
                "dtfac_precio_unitario": 0,
                "dtfac_iva": 0,
                "dtfac_total": 0,
                "aplicaImpuesto1": 1,
                "aplicaImpuesto2": 0,
                "aplicaImpuesto3": 0,
                "aplicaImpuesto4": 0,
                "aplicaImpuesto5": 0,
                "dtfac_valor_descuento": 0,
                "dtfac_porcentaje_descuento": 0,
                "dtfac_totaldesc": 0,
                "dtfac_ivadesc": 0,
                "dtfac_descripcion": "..KOLITA"        
            }
            ],
            "cliente": {
            "cliente_id": "C62EB822-216B-497A-8F61-AA1F2DD3945C",
            "cliente_documento": "V20289719",
            "cliente_nombres": "ALEJANDRO",
            "cliente_apellidos": "PEREZ",
            "cliente_telefono": "04241572784",
            "cliente_direccion": "NULL",
            "cliente_email": "AAA@INBOX.COM"
            },
            "formas_pago": [
            {
                "formapagoactura_id": "8FBF8DE7-5113-F111-ADF8-D0C1B5009507",
                "formapago_id": "5917064E-A357-EC11-94F6-0050F2D50918",
                "fpf_total_pagar": 4552.48,
                "formapago": "16"
            },
            {
                "formapagoactura_id": "8FBF8DE7-5113-F111-ADF8-D0C1B5009507",
                "formapago_id": "5917064E-A357-EC11-94F6-0050F2D50918",
                "fpf_total_pagar": 300.00,
                "formapago": "01"
            }
            ]
        }
        }


@pytest.fixture
def factura_sin_qr(factura_valida):
    """Factura sin QR"""
    data = factura_valida.copy()
    data['factura']['config_impresora']['impresion_qr'] = False
    return data


@pytest.fixture
def factura_sin_mensajes(factura_valida):
    """Factura sin mensajes"""
    data = factura_valida.copy()
    data['factura']['config_impresora']['impresion_msgqr'] = False
    return data


@pytest.fixture
def nota_credito_valida():
    """Fixture con datos de nota de crédito válida (con fecha)"""
    return {
        "nota_credito": {
            "config_impresora": {
                "impresion_qr": False,
                "impresion_msgqr": True,
                "impresion_cupon": False
            },
            "cabecera_factura": {
                "cabfact_id": "NC-001",
                "cabfact_subtotal": 50.00,
                "cabfact_iva": 9.50,
                "cabfact_total": 59.50,
                "cabfact_tasa_conversion": 1,
                "cabfact_fechacreacion": "2024-01-15 10:30:00"  # ← Agregar fecha
            },
            "cliente": {
                "cliente_documento": "9999999999999",
                "cliente_nombres": "CONSUMIDOR FINAL",
                "cliente_telefono": "000000000"
            },
            "detalle_factura": [],
            "formas_pago": []
        }
    }

@pytest.fixture
def mock_qr_service():
    """Fixture para mock de QRService"""
    with patch('server.services.qr_service.QRService') as mock:
        mock_instance = MagicMock()
        mock_instance.generar_trama_completa.return_value = "y1234567890"
        mock_instance.validar_impresion_qr.return_value = True
        mock.return_value = mock_instance
        yield mock_instance


@pytest.fixture
def mock_print_message_service():
    """Fixture para mock de PrintMessageService"""
    with patch('server.services.print_message_service.PrintMessageService') as mock:
        mock_instance = MagicMock()
        mock_instance.procesar_mensajes.return_value = {
            'success': True,
            'habilitado': True,
            'mensajes': ['i01Mensaje 1\n', 'i02Mensaje 2\n']
        }
        mock.return_value = mock_instance
        yield mock_instance

# tests/conftest.py - Agregar después de los fixtures existentes

@pytest.fixture
def factura_valida_data(factura_valida):
    """Fixture para datos de factura válida (sin envoltura)"""
    return factura_valida['factura']


@pytest.fixture
def factura_invalida_data():
    """Fixture para datos de factura inválida"""
    return {
        "config_impresora": {
            "impresion_qr": True,
            "impresion_msgqr": True,
            "impresion_cupon": False
        },
        "cabecera_factura": {
            "cabfact_id": "TEST-001",
            "cabfact_subtotal": 100,
            "cabfact_iva": 19,
            "cabfact_total": 200,  # Inconsistente
            "cabfact_tasa_conversion": 1,
            "cabfact_fechacreacion": "2024-01-15 10:30:00"
        },
        "cliente": {
            "cliente_documento": "",
            "cliente_nombres": "",
            "cliente_telefono": "123"
        },
        "detalle_factura": [],
        "formas_pago": []
    }


@pytest.fixture
def factura_diferencia_totales_data():
    """Fixture para factura con diferencia de totales"""
    return {
        "config_impresora": {
            "impresion_qr": True,
            "impresion_msgqr": True,
            "impresion_cupon": False
        },
        "cabecera_factura": {
            "cabfact_id": "TEST-001",
            "cabfact_subtotal": 100,
            "cabfact_iva": 19,
            "cabfact_total": 150,  # Diferencia
            "cabfact_tasa_conversion": 1,
            "cabfact_fechacreacion": "2024-01-15 10:30:00"
        },
        "cliente": {
            "cliente_documento": "9999999999999",
            "cliente_nombres": "TEST",
            "cliente_telefono": "123"
        },
        "detalle_factura": [],
        "formas_pago": []
    }


@pytest.fixture
def nota_credito_valida_data(nota_credito_valida):
    """Fixture para datos de nota crédito válida"""
    return nota_credito_valida['nota_credito']