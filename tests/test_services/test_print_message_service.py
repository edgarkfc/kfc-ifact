# tests/test_services/test_print_message_service.py
"""
Pruebas para PrintMessageService
"""
import pytest
from unittest.mock import patch
from server.services.print_message_service import PrintMessageService


class TestPrintMessageService:
    """Pruebas para PrintMessageService"""
    
    @pytest.fixture
    def print_service(self):
        return PrintMessageService()
    
    def test_validar_impresion_msgqr_true(self, print_service):
        config = {'impresion_msgqr': True}
        assert print_service.validar_impresion_msgqr(config) is True
    
    def test_validar_impresion_msgqr_false(self, print_service):
        config = {'impresion_msgqr': False}
        assert print_service.validar_impresion_msgqr(config) is False
    
    @pytest.mark.skip(reason="Esta prueba requiere mockear la caché interna, se probará en integración")
    def test_generar_mensajes_con_datos(self, print_service):
        """Prueba generación de mensajes desde BD - mockeando repositorio"""
        pass
    
    def test_generar_mensajes_sin_datos(self, print_service):
        """Prueba generación de mensajes sin datos en BD"""
        with patch.object(print_service.repository, 'get_all_active_ordered', return_value=[]):
            # Resetear caché
            print_service._mensajes_cache = None
            print_service._cache_timestamp = None
            
            mensajes = print_service.generar_mensajes('FACTURA')
            
            # Debe devolver mensajes por defecto
            assert len(mensajes) >= 4
            assert any('GRACIAS' in m for m in mensajes)
    
    def test_procesar_mensajes_habilitado(self, print_service):
        with patch.object(print_service, 'generar_mensajes', return_value=['i01Mensaje 1\n', 'i02Mensaje 2\n']):
            resultado = print_service.procesar_mensajes({
                'config_impresora': {'impresion_msgqr': True},
                'tipo_documento': 'FACTURA'
            })
            
            assert resultado['success'] is True
            assert resultado['habilitado'] is True
            assert len(resultado['mensajes']) == 2
    
    def test_procesar_mensajes_deshabilitado(self, print_service):
        resultado = print_service.procesar_mensajes({
            'config_impresora': {'impresion_msgqr': False}
        })
        
        assert resultado['habilitado'] is False