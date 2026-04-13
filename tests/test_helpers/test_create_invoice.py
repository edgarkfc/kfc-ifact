# tests/test_helpers/test_create_invoice.py
"""
Pruebas para helpers de create_invoice
"""

from server.controllers.helpers.create_invoice import (
    cabeceraFacturas,
    conversion_descuento_monto,
    format_decimal
)


class TestCreateInvoiceHelper:
    """Pruebas para helpers de create_invoice"""
    
    def test_cabecera_facturas_con_cliente(self):
        """Prueba generación de cabecera con cliente"""
        datos = {
            'cliente': {
                'cliente_nombres': 'JUAN PEREZ',
                'cliente_documento': '20123456789',
                'cliente_direccion': 'Av. Principal 123',
                'cliente_telefono': '0999999999'
            },
            'cabecera': {
                'cabfact_id': 'F001-001'
            }
        }
        
        resultado = cabeceraFacturas(datos)
        
        assert len(resultado) > 0
        assert 'JUAN PEREZ' in str(resultado)
    
    def test_cabecera_facturas_sin_cliente(self):
        """Prueba generación de cabecera sin cliente"""
        datos = {
            'cliente': {},
            'cabecera': {
                'cabfact_id': 'F001-001'
            }
        }
        
        resultado = cabeceraFacturas(datos)
        
        assert len(resultado) > 0
        assert 'CONSUMIDOR FINAL' in str(resultado)
    
    def test_conversion_descuento_monto_valor_positivo(self):
        """Prueba conversión de descuento positivo"""
        resultado = conversion_descuento_monto(100.50)
        
        assert len(resultado) == 9
        assert resultado.isdigit()
    
    def test_conversion_descuento_monto_valor_cero(self):
        """Prueba conversión de descuento cero"""
        resultado = conversion_descuento_monto(0)
        
        assert resultado == "000000000"
    
    def test_format_decimal(self):
        """Prueba formateo de decimales"""
        resultado = format_decimal(123.456, 2)
        assert '123.46' in resultado or '123,46' in resultado
    
    def test_format_decimal_sin_decimales(self):
        """Prueba formateo sin decimales"""
        resultado = format_decimal(123.456, 0, remove_decimal=True)
        assert resultado.isdigit()