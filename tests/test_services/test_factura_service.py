# tests/test_services/test_factura_service.py
"""
Pruebas para FacturaService
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from server.services.factura_service import FacturaService


class TestFacturaService:
    """Pruebas para FacturaService"""
    
    @pytest.fixture
    def factura_service(self):
        return FacturaService()
    
    def test_procesar_factura_valida(self, factura_service, factura_valida):
        """Prueba procesamiento de factura válida con datos reales"""
        datos = factura_valida['factura']
        
        # Parchear las clases importadas
        with patch('server.services.factura_service.ImpresionService') as MockImpresion:
            with patch('server.services.factura_service.QRService') as MockQR:
                with patch('server.services.print_message_service.PrintMessageService') as MockPrint:
                    
                    # Configurar mocks
                    mock_impresion = MockImpresion.return_value
                    mock_impresion.formatear_cabecera_con_cliente.return_value = ["iS* ALEJANDRO PEREZ\n"]
                    mock_impresion.formatear_producto.return_value = ("producto\n", {})
                    mock_impresion.agregar_linea_separador.return_value = "---\n"
                    mock_impresion.agregar_linea_final.return_value = "=== GRACIAS ===\n"
                    
                    mock_qr = MockQR.return_value
                    mock_qr.procesar_qr.return_value = {
                        'success': True, 'habilitado': True, 'qr_texto': 'y1234567890'
                    }
                    
                    mock_print = MockPrint.return_value
                    mock_print.procesar_mensajes.return_value = {
                        'success': True, 'habilitado': True, 'mensajes': []
                    }
                    
                    resultado = factura_service.procesar_factura({
                        'cabecera': datos.get('cabecera_factura', {}),
                        'cliente': datos.get('cliente', {}),
                        'detalle': datos.get('detalle_factura', []),
                        'formas_pago': datos.get('formas_pago', []),
                        'config_impresora': datos.get('config_impresora', {})
                    })
                    
                    assert resultado['tipo_documento'] == 'FACTURA'
                    assert 'factura_unificada' in resultado
                    assert 'metadata' in resultado
                    assert resultado['metadata']['total_factura'] == 4852.48
    
    def test_procesar_factura_sin_detalle(self, factura_service, factura_valida):
        """Prueba factura sin detalle"""
        datos = factura_valida['factura']
        
        with patch('server.services.factura_service.ImpresionService') as MockImpresion:
            with patch('server.services.print_message_service.PrintMessageService') as MockPrint:
                
                mock_impresion = MockImpresion.return_value
                mock_impresion.formatear_cabecera_con_cliente.return_value = ["iS* ALEJANDRO PEREZ\n"]
                mock_impresion.agregar_linea_separador.return_value = "---\n"
                mock_impresion.agregar_linea_final.return_value = "=== GRACIAS ===\n"
                
                mock_print = MockPrint.return_value
                mock_print.procesar_mensajes.return_value = {
                    'success': True, 'habilitado': True, 'mensajes': []
                }
                
                resultado = factura_service.procesar_factura({
                    'cabecera': datos.get('cabecera_factura', {}),
                    'cliente': datos.get('cliente', {}),
                    'detalle': [],
                    'formas_pago': datos.get('formas_pago', []),
                    'config_impresora': datos.get('config_impresora', {})
                })
                
                assert resultado['metadata']['total_items'] == 0
    
    def test_procesar_factura_con_error(self, factura_service):
        """Prueba manejo de errores"""
        with pytest.raises(Exception):
            factura_service.procesar_factura(None)