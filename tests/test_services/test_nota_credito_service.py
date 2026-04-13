# tests/test_services/test_nota_credito_service.py
"""
Pruebas para NotaCreditoService
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from server.services.nota_credito_service import NotaCreditoService


class TestNotaCreditoService:
    """Pruebas para NotaCreditoService"""
    
    @pytest.fixture
    def nota_credito_service(self):
        """Fixture del servicio"""
        return NotaCreditoService()
    
    def test_procesar_nota_credito_valida(self, nota_credito_service, nota_credito_valida):
        """Prueba procesamiento de nota crédito válida"""
        datos = nota_credito_valida['nota_credito']
        
        resultado = nota_credito_service.procesar_nota_credito({
            'cabecera': datos.get('cabecera_factura', {}),
            'cliente': datos.get('cliente', {}),
            'detalle': datos.get('detalle_factura', []),
            'formas_pago': datos.get('formas_pago', []),
            'config_impresora': datos.get('config_impresora', {})
        })
        
        assert resultado['tipo_documento'] == 'NOTA_CREDITO'
        assert 'factura_unificada' in resultado
        assert 'metadata' in resultado
    
    def test_procesar_nota_credito_sin_qr(self, nota_credito_service, nota_credito_valida):
        """Prueba que nota crédito NO tiene QR"""
        datos = nota_credito_valida['nota_credito']
        
        resultado = nota_credito_service.procesar_nota_credito({
            'cabecera': datos.get('cabecera_factura', {}),
            'cliente': datos.get('cliente', {}),
            'detalle': datos.get('detalle_factura', []),
            'formas_pago': datos.get('formas_pago', []),
            'config_impresora': datos.get('config_impresora', {})
        })
        
        # Verificar que no hay QR (no hay línea que empiece con 'y')
        factura_unificada = resultado['factura_unificada']
        tiene_qr = any(linea.startswith('y') for linea in factura_unificada if isinstance(linea, str))
        assert tiene_qr is False
    
    def test_procesar_nota_credito_con_error(self, nota_credito_service):
        """Prueba manejo de errores"""
        with pytest.raises(Exception):
            nota_credito_service.procesar_nota_credito(None)