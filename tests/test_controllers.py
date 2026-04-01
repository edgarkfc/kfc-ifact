import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from marshmallow import ValidationError
from server.controllers.bills_controller import (
    validar_factura,
    procesar_factura,
    armar_factura,
    validar_factura_controller,
    procesar_factura_controller,
    armar_factura_controller,
    health_check_controller
)

class TestControllers:
    """Tests para los controladores"""
    
    def test_validar_factura_exito(self, factura_valida_data):
        """Test validación exitosa de factura"""
        datos_validados = validar_factura(factura_valida_data)
        
        assert datos_validados is not None
        # El schema transforma los nombres: cabecera_factura -> cabecera
        assert 'cliente' in datos_validados
        assert 'cabecera' in datos_validados  # ← Cambiado de cabecera_factura a cabecera
        assert 'detalle' in datos_validados   # ← Cambiado de detalle_factura a detalle
        
        # Verificar que los totales sean correctos
        cabecera = datos_validados['cabecera']
        total_cabecera = cabecera.get('cabfact_total', 0)
        subtotal_cabecera = cabecera.get('cabfact_subtotal', 0)
        iva_cabecera = cabecera.get('cabfact_iva', 0)
        
        # Verificar relación: total = subtotal + iva
        assert abs((subtotal_cabecera + iva_cabecera) - total_cabecera) <= 0.05
    
    def test_validar_factura_error(self, factura_invalida_data):
        """Test validación con error"""
        with pytest.raises(ValidationError) as exc_info:
            validar_factura(factura_invalida_data)
        
        # Debería tener error en cabecera_factura
        assert 'cabecera_factura' in exc_info.value.messages
    
    def test_procesar_factura_exito(self, factura_valida_data,
                                     mock_print_message, 
                                     mock_cabeceraFacturas,
                                     mock_factura_productos,
                                     mock_factura_pagos,
                                     mock_validar_mensaje_qr):
        """Test procesamiento exitoso de factura con mocks"""
        # Primero validar - usar factura válida simple
        datos_validados = validar_factura(factura_valida_data)
        
        # Luego procesar
        resultado = procesar_factura(datos_validados)
        
        assert resultado is not None
        assert 'cabecera_cliente' in resultado
        assert 'detail_productos' in resultado
        assert 'pagos_factura' in resultado
        assert 'factura_unificada' in resultado
        assert 'metadata' in resultado
        assert isinstance(resultado['factura_unificada'], list)
        assert len(resultado['factura_unificada']) > 0
    
    def test_armar_factura_exito(self, factura_valida_data,
                                  mock_print_message,
                                  mock_cabeceraFacturas,
                                  mock_factura_productos,
                                  mock_factura_pagos,
                                  mock_validar_mensaje_qr):
        """Test armar factura exitoso (compatibilidad)"""
        resultado = armar_factura(factura_valida_data)
        
        assert resultado is not None
        assert 'error' not in resultado
        assert 'factura_unificada' in resultado
        assert isinstance(resultado['factura_unificada'], list)
    
    def test_armar_factura_error(self, factura_invalida_data):
        """Test armar factura con error (compatibilidad)"""
        resultado = armar_factura(factura_invalida_data)
        
        assert resultado is not None
        assert 'error' in resultado
        assert resultado['error'] == 'validacion_fallida'
    
    def test_validar_factura_controller_exito(self, factura_valida_data):
        """Test controller de validación exitoso"""
        respuesta, error, status_code = validar_factura_controller(factura_valida_data)
        
        assert status_code == 200
        assert error is None
        assert respuesta['success'] is True
        assert respuesta['message'] == 'Factura válida'
        assert 'data' in respuesta
    
    def test_validar_factura_controller_error(self, factura_invalida_data):
        """Test controller de validación con error"""
        respuesta, error, status_code = validar_factura_controller(factura_invalida_data)
        
        assert status_code == 422
        assert error is not None
        assert respuesta['success'] is False
        assert respuesta['message'] == 'Error de validación en la factura'
        assert 'errors' in respuesta
    
    def test_procesar_factura_controller_exito(self, factura_valida_data,
                                                mock_print_message,
                                                mock_cabeceraFacturas,
                                                mock_factura_productos,
                                                mock_factura_pagos,
                                                mock_validar_mensaje_qr):
        """Test controller de procesamiento exitoso"""
        respuesta, error, status_code = procesar_factura_controller(factura_valida_data)
        
        assert status_code == 200
        assert error is None
        assert respuesta['success'] is True
        assert respuesta['message'] == 'Factura procesada exitosamente'
        assert 'data' in respuesta
        assert 'factura_unificada' in respuesta['data']
    
    def test_procesar_factura_controller_error(self, factura_invalida_data):
        """Test controller de procesamiento con error"""
        respuesta, error, status_code = procesar_factura_controller(factura_invalida_data)
        
        assert status_code == 422
        assert error is not None
        assert respuesta['success'] is False
        assert respuesta['message'] == 'Error de validación'
        assert 'errors' in respuesta
    
    def test_armar_factura_controller_exito(self, factura_valida_data,
                                             mock_print_message,
                                             mock_cabeceraFacturas,
                                             mock_factura_productos,
                                             mock_factura_pagos,
                                             mock_validar_mensaje_qr):
        """Test controller armar factura exitoso"""
        respuesta, error, status_code = armar_factura_controller(factura_valida_data)
        
        assert status_code == 200
        assert error is None
        assert respuesta['success'] is True
        assert respuesta['message'] == 'Factura armada exitosamente'
        assert 'data' in respuesta
    
    def test_armar_factura_controller_error(self, factura_invalida_data):
        """Test controller armar factura con error"""
        respuesta, error, status_code = armar_factura_controller(factura_invalida_data)
        
        assert status_code == 422
        assert error is not None
        assert respuesta['success'] is False
    
    def test_health_check_controller(self):
        """Test health check controller"""
        respuesta, status_code = health_check_controller()
        
        assert status_code == 200
        assert respuesta['success'] is True
        assert respuesta['message'] == 'Servicio de facturas operativo'
        assert respuesta['version'] == '1.0.0'