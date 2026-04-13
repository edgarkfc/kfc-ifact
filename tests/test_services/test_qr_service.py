# tests/test_services/test_qr_service.py
"""
Pruebas para QRService
"""
import pytest
from unittest.mock import patch, MagicMock
from server.services.qr_service import QRService


class TestQRService:
    """Pruebas para QRService"""
    
    @pytest.fixture
    def qr_service(self):
        """Fixture del servicio QR"""
        return QRService()
    
    def test_validar_impresion_qr_true(self, qr_service):
        """Prueba validación QR habilitado"""
        config = {'impresion_qr': True}
        assert qr_service.validar_impresion_qr(config) is True
    
    def test_validar_impresion_qr_false(self, qr_service):
        """Prueba validación QR deshabilitado"""
        config = {'impresion_qr': False}
        assert qr_service.validar_impresion_qr(config) is False
    
    def test_validar_impresion_qr_sin_config(self, qr_service):
        """Prueba validación sin configuración"""
        config = {}
        assert qr_service.validar_impresion_qr(config) is False
    
    def test_generar_trama_completa_formato(self, qr_service):
        """Prueba formato de trama QR"""
        with patch('server.services.qr_service.QRService.generar_trama_numerica') as mock_trama:
            mock_trama.return_value = "1234567890"
            trama = qr_service.generar_trama_completa()
            
            assert trama is not None
            assert trama[0] == 'y'
            # Limpiar el string de posibles saltos de línea
            trama_limpia = trama.strip()
            assert trama_limpia[1:].isdigit()
    
    def test_procesar_qr_habilitado(self, qr_service):
        """Prueba procesamiento QR habilitado"""
        with patch('server.services.qr_service.QRService.generar_trama_completa') as mock_trama:
            mock_trama.return_value = "y1234567890"
            
            resultado = qr_service.procesar_qr({
                'config_impresora': {'impresion_qr': True}
            })
            
            assert resultado['success'] is True
            assert resultado['habilitado'] is True
            assert resultado['qr_texto'] == "y1234567890"
    
    def test_procesar_qr_deshabilitado(self, qr_service):
        """Prueba procesamiento QR deshabilitado"""
        resultado = qr_service.procesar_qr({
            'config_impresora': {'impresion_qr': False}
        })
        
        assert resultado['habilitado'] is False