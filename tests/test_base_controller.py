# tests/test_base_controller.py
"""
Pruebas para BaseController
"""
import pytest
from unittest.mock import Mock, patch
from marshmallow import ValidationError

from server.controllers.base_controller import DocumentoBaseController


class MockSchema:
    """Schema mock para pruebas"""
    def load(self, data):
        if data.get('error'):
            raise ValidationError("Error de validación")
        return data


class MockController(DocumentoBaseController):
    """Controlador mock para pruebas"""
    
    def __init__(self):
        super().__init__(MockSchema)
        self.tipo_documento = "TEST"
    
    def procesar_documento(self, datos_validados):
        return {"procesado": True, "datos": datos_validados}
    
    def _obtener_resumen(self, datos_validados):
        return {"resumen": "test"}


class TestBaseController:
    """Pruebas para BaseController"""
    
    @pytest.fixture
    def controller(self):
        return MockController()
    
    def test_validar_documento_exitoso(self, controller):
        """Prueba validación exitosa"""
        datos = {"test": "data"}
        resultado = controller.validar_documento(datos)
        assert resultado == datos
    
    def test_validar_documento_con_error(self, controller):
        """Prueba validación con error"""
        datos = {"error": True}
        with pytest.raises(ValidationError):
            controller.validar_documento(datos)
    
    def test_procesar_controller_exitoso(self, controller):
        """Prueba procesar controller exitoso"""
        datos = {"test": "data"}
        respuesta, error, status = controller.procesar_controller(datos)
        
        assert status == 200
        assert respuesta['success'] is True
        assert error is None
        assert 'data' in respuesta
    
    def test_procesar_controller_con_validacion_error(self, controller):
        """Prueba procesar controller con error de validación"""
        datos = {"error": True}
        respuesta, error, status = controller.procesar_controller(datos)
        
        assert status == 422
        assert respuesta['success'] is False
        assert error is not None
    
    def test_procesar_controller_con_error_general(self, controller):
        """Prueba procesar controller con error general"""
        with patch.object(controller, 'validar_documento', side_effect=Exception("Error inesperado")):
            respuesta, error, status = controller.procesar_controller({})
            
            assert status == 500
            assert respuesta['success'] is False