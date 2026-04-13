# tests/test_controllers.py
"""
Pruebas para controladores
"""
import pytest
from unittest.mock import patch

from server.controllers.bills_controller import (
    procesar_factura_controller  # Solo procesar existe ahora
)
from server.controllers.notas_credito_module import (
    procesar_nota_credito_controller  # Solo procesar existe ahora
)


class TestBillsController:
    """Pruebas para controlador de facturas"""
    
    @pytest.fixture
    def datos_factura_valida(self, factura_valida):
        """Datos de factura válida"""
        return factura_valida['factura']
    
    def test_procesar_factura_controller_exitoso(self, datos_factura_valida):
        """Prueba procesar factura exitoso"""
        with patch('server.controllers.bills_controller._factura_controller') as mock_controller:
            mock_controller.procesar_controller.return_value = (
                {'success': True, 'message': 'FACTURA procesada', 'data': {}},
                None,
                200
            )
            
            respuesta, error, status = procesar_factura_controller(datos_factura_valida)
            
            assert status == 200
            assert respuesta['success'] is True
            assert error is None
    
    def test_procesar_factura_controller_error(self):
        """Prueba procesar factura con error"""
        with patch('server.controllers.bills_controller._factura_controller') as mock_controller:
            mock_controller.procesar_controller.return_value = (
                {'success': False, 'message': 'Error'},
                Exception('Error'),
                500
            )
            
            respuesta, error, status = procesar_factura_controller({})
            
            assert status == 500
            assert respuesta['success'] is False
            assert error is not None


class TestNotasCreditoController:
    """Pruebas para controlador de notas de crédito"""
    
    @pytest.fixture
    def datos_nota_valida(self, nota_credito_valida):
        """Datos de nota de crédito válida"""
        return nota_credito_valida['nota_credito']
    
    def test_procesar_nota_credito_controller_exitoso(self, datos_nota_valida):
        """Prueba procesar nota crédito exitoso"""
        with patch('server.controllers.notas_credito_module._nota_credito_controller') as mock_controller:
            mock_controller.procesar_controller.return_value = (
                {'success': True, 'message': 'NOTA_CREDITO procesada', 'data': {}},
                None,
                200
            )
            
            respuesta, error, status = procesar_nota_credito_controller(datos_nota_valida)
            
            assert status == 200
            assert respuesta['success'] is True
    
    def test_procesar_nota_credito_controller_error(self):
        """Prueba procesar nota crédito con error"""
        with patch('server.controllers.notas_credito_module._nota_credito_controller') as mock_controller:
            mock_controller.procesar_controller.return_value = (
                {'success': False, 'message': 'Error'},
                Exception('Error'),
                500
            )
            
            respuesta, error, status = procesar_nota_credito_controller({})
            
            assert status == 500
            assert respuesta['success'] is False