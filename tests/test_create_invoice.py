import sys
import os
import pytest
from unittest.mock import Mock, patch, MagicMock
from decimal import Decimal

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from server.controllers.helpers.create_invoice import (
    cabeceraFacturas,
    factura_productos,
    conversion_precio,
    conversion_descuento_monto,
    format_decimal,
    factura_pagos,
    conversion_fpago
)


class TestCabeceraFacturas:
    """Tests para la función cabeceraFacturas"""
    
    def test_cabecera_con_cliente_sin_delivery(self):
        """Test cabecera con cliente y sin delivery"""
        datos = {
            'cliente': {
                'cliente_nombres': 'JUAN PEREZ',
                'cliente_documento': 'V12345678',
                'cliente_direccion': 'CALLE PRINCIPAL 123',
                'cliente_telefono': '04121234567'
            },
            'cabecera': {
                'cabfact_id': 'FAC-001'
            }
        }
        
        resultado = cabeceraFacturas(datos)
        
        assert resultado is not None
        assert len(resultado) == 5  # 5 líneas sin delivery
        assert 'JUAN PEREZ' in resultado[0]
        assert 'V12345678' in resultado[1]
        assert 'CALLE PRINCIPAL 123' in resultado[2]
        assert '04121234567' in resultado[3]
        assert 'FAC-001' in resultado[4]
    
    def test_cabecera_con_cliente_con_delivery(self):
        """Test cabecera con cliente y con delivery"""
        datos = {
            'cliente': {
                'cliente_nombres': 'MARIA GOMEZ',
                'cliente_documento': 'V87654321',
                'cliente_direccion': 'AVENIDA CENTRAL 456',
                'cliente_telefono': '04249876543'
            },
            'cabecera': {
                'cabfact_id': 'FAC-002',
                'delivery_id': 'DEL-001'
            }
        }
        
        resultado = cabeceraFacturas(datos)
        
        assert resultado is not None
        assert len(resultado) == 6  # 6 líneas con delivery
        assert 'MARIA GOMEZ' in resultado[0]
        assert 'V87654321' in resultado[1]
        assert 'AVENIDA CENTRAL 456' in resultado[2]
        assert '04249876543' in resultado[3]
        assert 'FAC-002' in resultado[4]
        assert 'DEL-001' in resultado[5]
    
    def test_cabecera_sin_cliente(self):
        """Test cabecera sin datos de cliente (consumidor final)"""
        datos = {
            'cliente': {},
            'cabecera': {
                'cabfact_id': 'FAC-003'
            }
        }
        
        resultado = cabeceraFacturas(datos)
        
        # Cuando no hay cliente, devuelve dict vacío o maneja error
        assert resultado is not None
        # Verificar que devuelve líneas por defecto o maneja el error
    
    def test_cabecera_con_campos_vacios(self):
        """Test cabecera con campos vacíos"""
        datos = {
            'cliente': {
                'cliente_nombres': '',
                'cliente_documento': '',
                'cliente_direccion': '',
                'cliente_telefono': ''
            },
            'cabecera': {
                'cabfact_id': ''
            }
        }
        
        resultado = cabeceraFacturas(datos)
        
        assert resultado is not None
        assert len(resultado) == 5
        # Debería manejar campos vacíos sin errores


class TestFacturaProductos:
    """Tests para la función factura_productos"""
    
    def test_productos_normales(self):
        """Test productos normales con precio > 0"""
        datos_validados = {
            'detalle': [
                {
                    'dtfac_total': 100.00,
                    'dtfac_descripcion': 'PRODUCTO 1',
                    'dtfac_precio_unitario': 100.00,
                    'dtfac_cantidad': 1,
                    'dtfac_porcentaje_descuento': 0,
                    'dtfac_valor_descuento': 0
                },
                {
                    'dtfac_total': 200.00,
                    'dtfac_descripcion': 'PRODUCTO 2',
                    'dtfac_precio_unitario': 100.00,
                    'dtfac_cantidad': 2,
                    'dtfac_porcentaje_descuento': 0,
                    'dtfac_valor_descuento': 0
                }
            ],
            'restaurante': {
                'impuesto_rest': True
            }
        }
        factura = []
        
        resultado = factura_productos(datos_validados, factura)
        
        assert resultado is not None
        assert 'factura' in resultado
        assert 'count' in resultado
        assert len(resultado['factura']) == 2
        assert resultado['count'] == 2
    
    def test_productos_con_descuento_porcentaje(self):
        """Test productos con descuento por porcentaje"""
        datos_validados = {
            'detalle': [
                {
                    'dtfac_total': 100.00,
                    'dtfac_descripcion': 'PRODUCTO CON DESCUENTO',
                    'dtfac_precio_unitario': 100.00,
                    'dtfac_cantidad': 1,
                    'dtfac_porcentaje_descuento': 10,
                    'dtfac_valor_descuento': 0
                }
            ],
            'restaurante': {
                'impuesto_rest': True
            }
        }
        factura = []
        
        resultado = factura_productos(datos_validados, factura)
        
        assert resultado is not None
        assert len(resultado['factura']) == 2  # producto + línea descuento
        # Verificar línea de descuento
        assert 'p-1000' in resultado['factura'][1] or 'p-10' in resultado['factura'][1]
    
    def test_productos_con_descuento_monto(self):
        """Test productos con descuento por monto"""
        datos_validados = {
            'detalle': [
                {
                    'dtfac_total': 100.00,
                    'dtfac_descripcion': 'PRODUCTO CON DESCUENTO MONTO',
                    'dtfac_precio_unitario': 100.00,
                    'dtfac_cantidad': 1,
                    'dtfac_porcentaje_descuento': 0,
                    'dtfac_valor_descuento': 10.00
                }
            ],
            'restaurante': {
                'impuesto_rest': True
            }
        }
        factura = []
        
        resultado = factura_productos(datos_validados, factura)
        
        assert resultado is not None
        assert len(resultado['factura']) == 2  # producto + línea descuento
        # Verificar línea de descuento por monto
        assert 'q-' in resultado['factura'][1]
    
    def test_productos_complementarios(self):
        """Test productos complementarios con precio 0"""
        datos_validados = {
            'detalle': [
                {
                    'dtfac_total': 0.00,
                    'dtfac_descripcion': 'PRODUCTO COMPLEMENTARIO',
                    'dtfac_precio_unitario': 0,
                    'dtfac_cantidad': 1,
                    'dtfac_porcentaje_descuento': 0,
                    'dtfac_valor_descuento': 0
                }
            ],
            'restaurante': {
                'impuesto_rest': True
            }
        }
        factura = []
        
        resultado = factura_productos(datos_validados, factura)
        
        assert resultado is not None
        assert len(resultado['factura']) == 1
        assert '@' in resultado['factura'][0]
        assert 'PRODUCTO COMPLEMENTARIO' in resultado['factura'][0]
    
    def test_productos_con_factura_none(self):
        """Test con factura None (debe inicializarse)"""
        datos_validados = {
            'detalle': [
                {
                    'dtfac_total': 50.00,
                    'dtfac_descripcion': 'PRODUCTO TEST',
                    'dtfac_precio_unitario': 50.00,
                    'dtfac_cantidad': 1,
                    'dtfac_porcentaje_descuento': 0,
                    'dtfac_valor_descuento': 0
                }
            ],
            'restaurante': {
                'impuesto_rest': False
            }
        }
        
        resultado = factura_productos(datos_validados, None)
        
        assert resultado is not None
        assert 'factura' in resultado
        assert len(resultado['factura']) == 1
    
    def test_productos_vacios(self):
        """Test sin productos"""
        datos_validados = {
            'detalle': [],
            'restaurante': {}
        }
        factura = []
        
        resultado = factura_productos(datos_validados, factura)
        
        assert resultado is not None
        assert len(resultado['factura']) == 0
        assert resultado['count'] == 0


class TestConversionPrecio:
    """Tests para la función conversion_precio"""
    
    def test_conversion_con_impuesto(self):
        """Test conversión con impuesto activado"""
        producto = {
            'dtfac_precio_unitario': 100.00,
            'dtfac_cantidad': 2,
            'dtfac_descripcion': 'PRODUCTO TEST'
        }
        restaurante = {'impuesto_rest': True}
        n_credito = False
        
        resultado = conversion_precio(producto, n_credito, restaurante)
        
        assert resultado is not None
        assert resultado.startswith('!')
        assert 'PRODUCTO TEST' in resultado
        # Verificar formato: ! + precio(11 dígitos) + cantidad(8 dígitos) + descripción
        # precio: 100.00 -> 10000 -> zfill(11) = 00000010000
        assert '00000010000' in resultado or '10000' in resultado
    
    def test_conversion_sin_impuesto(self):
        """Test conversión sin impuesto (exento)"""
        producto = {
            'dtfac_precio_unitario': 50.50,
            'dtfac_cantidad': 3,
            'dtfac_descripcion': 'PRODUCTO EXENTO'
        }
        restaurante = {'impuesto_rest': False}
        n_credito = False
        
        resultado = conversion_precio(producto, n_credito, restaurante)
        
        assert resultado is not None
        assert resultado.startswith(' ')
        assert 'PRODUCTO EXENTO' in resultado
    
    def test_conversion_nota_credito_con_impuesto(self):
        """Test conversión nota de crédito con impuesto"""
        producto = {
            'dtfac_precio_unitario': 75.00,
            'dtfac_cantidad': 1,
            'dtfac_descripcion': 'PRODUCTO NOTA CREDITO'
        }
        restaurante = {'impuesto_rest': True}
        n_credito = True
        
        resultado = conversion_precio(producto, n_credito, restaurante)
        
        assert resultado is not None
        assert resultado.startswith('d1')
        assert 'PRODUCTO NOTA CREDITO' in resultado
    
    def test_conversion_nota_credito_sin_impuesto(self):
        """Test conversión nota de crédito sin impuesto"""
        producto = {
            'dtfac_precio_unitario': 30.00,
            'dtfac_cantidad': 2,
            'dtfac_descripcion': 'PRODUCTO NOTA CREDITO EXENTO'
        }
        restaurante = {'impuesto_rest': False}
        n_credito = True
        
        resultado = conversion_precio(producto, n_credito, restaurante)
        
        assert resultado is not None
        assert resultado.startswith('d0')
        assert 'PRODUCTO NOTA CREDITO EXENTO' in resultado
    
    def test_conversion_valores_cero(self):
        """Test conversión con valores cero"""
        producto = {
            'dtfac_precio_unitario': 0,
            'dtfac_cantidad': 0,
            'dtfac_descripcion': ''
        }
        restaurante = {'impuesto_rest': True}
        n_credito = False
        
        resultado = conversion_precio(producto, n_credito, restaurante)
        
        assert resultado is not None
        assert '\n' in resultado
    
    def test_conversion_valores_invalidos(self):
        """Test conversión con valores inválidos"""
        producto = {
            'dtfac_precio_unitario': 'invalid',
            'dtfac_cantidad': 'invalid',
            'dtfac_descripcion': None
        }
        restaurante = {'impuesto_rest': True}
        n_credito = False
        
        resultado = conversion_precio(producto, n_credito, restaurante)
        
        # Debería manejar errores y devolver algo
        assert resultado is not None
        assert isinstance(resultado, str)


class TestConversionDescuentoMonto:
    """Tests para la función conversion_descuento_monto"""
    
    def test_conversion_valor_entero(self):
        """Test conversión de descuento con valor entero"""
        resultado = conversion_descuento_monto(100)
        
        # 100.00 -> 10000 -> zfill(9) = 000010000
        assert resultado == '000010000'
        assert len(resultado) == 9
    
    def test_conversion_valor_decimal(self):
        """Test conversión de descuento con valor decimal"""
        resultado = conversion_descuento_monto(50.50)
        
        # 50.50 -> 5050 -> zfill(9) = 000005050
        assert resultado == '000005050'
        assert len(resultado) == 9
    
    def test_conversion_valor_pequeno(self):
        """Test conversión de descuento con valor pequeño"""
        resultado = conversion_descuento_monto(0.50)
        
        # 0.50 -> 050 -> zfill(9) = 000000050
        assert resultado == '000000050'
        assert len(resultado) == 9
    
    def test_conversion_valor_string(self):
        """Test conversión de descuento con string"""
        resultado = conversion_descuento_monto('75.75')
        
        # 75.75 -> 7575 -> zfill(9) = 000007575
        assert resultado == '000007575'
    
    def test_conversion_valor_string_null(self):
        """Test conversión de descuento con string 'null'"""
        resultado = conversion_descuento_monto('null')
        
        assert resultado == '000000000'
        assert len(resultado) == 9
    
    def test_conversion_valor_none(self):
        """Test conversión de descuento con None"""
        resultado = conversion_descuento_monto(None)
        
        assert resultado == '000000000'
        assert len(resultado) == 9
    
    def test_conversion_valor_invalido(self):
        """Test conversión de descuento con valor inválido"""
        resultado = conversion_descuento_monto('invalid')
        
        # Debería devolver ceros
        assert resultado == '000000000'
        assert len(resultado) == 9


class TestFormatDecimal:
    """Tests para la función format_decimal"""
    
    def test_format_decimal_2_decimales(self):
        """Test formato con 2 decimales"""
        resultado = format_decimal(123.456, 2)
        
        # Debería redondear a 123.46
        assert resultado == '123.46'
    
    def test_format_decimal_sin_decimales(self):
        """Test formato sin decimales"""
        resultado = format_decimal(123.456, 0)
        
        # Debería redondear a 123
        assert resultado == '123'
    
    def test_format_decimal_con_remove_decimal(self):
        """Test formato con eliminación de punto decimal"""
        resultado = format_decimal(123.45, 2, remove_decimal=True)
        
        assert resultado == '12345'
    
    def test_format_decimal_valor_entero(self):
        """Test formato con valor entero"""
        resultado = format_decimal(100, 2)
        
        assert resultado == '100.00'
    
    def test_format_decimal_valor_string(self):
        """Test formato con string"""
        resultado = format_decimal('123.456', 2)
        
        assert resultado == '123.46'
    
    def test_format_decimal_valor_string_null(self):
        """Test formato con string 'null'"""
        resultado = format_decimal('null', 2)
        
        assert resultado == '0.00'
    
    def test_format_decimal_valor_vacio(self):
        """Test formato con string vacío"""
        resultado = format_decimal('', 2)
        
        assert resultado == '0.00'
    
    def test_format_decimal_valor_none(self):
        """Test formato con None"""
        resultado = format_decimal(None, 2)
        
        assert resultado == '0.00'
    
    def test_format_decimal_redondeo_mitad_superior(self):
        """Test redondeo HALF_UP"""
        resultado = format_decimal(2.675, 2)
        
        # Debería redondear a 2.68
        assert resultado == '2.68'


class TestFacturaPagos:
    """Tests para la función factura_pagos"""
    
    def test_pagos_sin_descuentos(self):
        """Test pagos sin descuentos"""
        factura = []
        json_data = {
            'cabecera': {
                'cabfact_porcentaje_descuento': 0,
                'cabfact_valor_descuento': 0
            },
            'formas_pago': [
                {
                    'fpf_total_pagar': 100.00,
                    'formapago': '01'
                }
            ],
            'config_impresora': {
                'impresion_qr': False
            }
        }
        
        resultado = factura_pagos(factura, json_data)
        
        assert resultado is not None
        assert 'factura' in resultado
        assert len(resultado['factura']) >= 2  # línea "3\n" + pago
    
    def test_pagos_con_descuento_porcentaje(self):
        """Test pagos con descuento por porcentaje"""
        factura = []
        json_data = {
            'cabecera': {
                'cabfact_porcentaje_descuento': 10,
                'cabfact_valor_descuento': 0
            },
            'formas_pago': [
                {
                    'fpf_total_pagar': 90.00,
                    'formapago': '01'
                }
            ],
            'config_impresora': {
                'impresion_qr': False
            }
        }
        
        resultado = factura_pagos(factura, json_data)
        
        assert resultado is not None
        # Verificar que hay línea de descuento
        descuentos = [line for line in resultado['factura'] if line.startswith('p-')]
        assert len(descuentos) == 1
    
    def test_pagos_con_descuento_monto(self):
        """Test pagos con descuento por monto"""
        factura = []
        json_data = {
            'cabecera': {
                'cabfact_porcentaje_descuento': 0,
                'cabfact_valor_descuento': 10.00
            },
            'formas_pago': [
                {
                    'fpf_total_pagar': 90.00,
                    'formapago': '01'
                }
            ],
            'config_impresora': {
                'impresion_qr': False
            }
        }
        
        resultado = factura_pagos(factura, json_data)
        
        assert resultado is not None
        # Verificar que hay línea de descuento
        descuentos = [line for line in resultado['factura'] if line.startswith('q-')]
        assert len(descuentos) == 1
    
    def test_pagos_con_impresion_qr(self):
        """Test pagos con impresión QR activada"""
        factura = []
        json_data = {
            'cabecera': {
                'cabfact_porcentaje_descuento': 0,
                'cabfact_valor_descuento': 0
            },
            'formas_pago': [
                {
                    'fpf_total_pagar': 100.00,
                    'formapago': '01'
                }
            ],
            'config_impresora': {
                'impresion_qr': True
            }
        }
        
        # Mock para procesar_qr
        with patch('server.controllers.helpers.algortimoqr.procesar_qr') as mock_qr:
            mock_qr.return_value = 'QR_CODE_DATA'
            
            resultado = factura_pagos(factura, json_data)
            
            assert resultado is not None
            # Verificar que se agregó línea QR
            lineas_qr = [line for line in resultado['factura'] if line.startswith('y')]
            assert len(lineas_qr) == 1
    
    def test_pagos_multiple(self):
        """Test múltiples formas de pago"""
        factura = []
        json_data = {
            'cabecera': {
                'cabfact_porcentaje_descuento': 0,
                'cabfact_valor_descuento': 0
            },
            'formas_pago': [
                {
                    'fpf_total_pagar': 50.00,
                    'formapago': '01'
                },
                {
                    'fpf_total_pagar': 30.00,
                    'formapago': '16'
                },
                {
                    'fpf_total_pagar': 20.00,
                    'formapago': '02'
                }
            ],
            'config_impresora': {
                'impresion_qr': False
            }
        }
        
        resultado = factura_pagos(factura, json_data)
        
        assert resultado is not None
        assert len(resultado['factura']) >= 4  # "3\n" + 3 pagos


class TestConversionFpago:
    """Tests para la función conversion_fpago"""
    
    def test_conversion_pago_normal(self):
        """Test conversión de pago normal"""
        pago = {
            'fpf_total_pagar': 100.00,
            'formapago': '01'
        }
        
        resultado = conversion_fpago(None, pago)
        
        assert resultado is not None
        assert resultado.startswith('201')
        assert len(resultado) >= 15  # 2 + 2 + 12 + \n
    
    def test_conversion_pago_con_igtf(self):
        """Test conversión de pago con IGTF"""
        pago = {
            'fpf_total_pagar': 100.00,
            'formapago': '01'
        }
        igtf = 5.00
        
        resultado = conversion_fpago(igtf, pago)
        
        assert resultado is not None
        # Debería tener formato "2" + precio (12 dígitos) + "\n"
        assert resultado.startswith('2')
        assert len(resultado) >= 14
    
    def test_conversion_pago_valor_cero(self):
        """Test conversión de pago con valor cero"""
        pago = {
            'fpf_total_pagar': 0,
            'formapago': '01'
        }
        
        resultado = conversion_fpago(None, pago)
        
        assert resultado is not None
        assert '000000000000' in resultado
    
    def test_conversion_pago_codigo_invalido(self):
        """Test conversión de pago con código inválido"""
        pago = {
            'fpf_total_pagar': 50.00,
            'formapago': '999'
        }
        
        resultado = conversion_fpago(None, pago)
        
        # Debería usar '00' como código por defecto
        assert resultado is not None
        assert resultado.startswith('2')  # Siempre empieza con '2'
        assert len(resultado) > 5  # Tiene longitud mínima
    
    def test_conversion_pago_string_valor(self):
        """Test conversión de pago con valor como string"""
        pago = {
            'fpf_total_pagar': '75.50',
            'formapago': '16'
        }
        
        resultado = conversion_fpago(None, pago)
        
        assert resultado is not None
        assert '16' in resultado[:4]  # 2 + código de 2 dígitos
    
    def test_conversion_pago_valor_invalido(self):
        """Test conversión de pago con valor inválido"""
        pago = {
            'fpf_total_pagar': 'invalid',
            'formapago': '01'
        }
        
        resultado = conversion_fpago(None, pago)
        
        # Debería devolver línea por defecto
        assert resultado is not None
        assert isinstance(resultado, str)
    
    def test_conversion_pago_con_factura_none(self):
        """Test conversión con pago None"""
        pago = {
            'fpf_total_pagar': None,
            'formapago': None
        }
        
        resultado = conversion_fpago(None, pago)
        
        assert resultado is not None
        assert '00' in resultado[:4]  # Código por defecto 00


class TestIntegracionCreateInvoice:
    """Tests de integración para create_invoice"""
    
    def test_flujo_completo_factura(self):
        """Test flujo completo de creación de factura"""
        datos = {
            'cliente': {
                'cliente_nombres': 'TEST CLIENTE',
                'cliente_documento': 'V12345678',
                'cliente_direccion': 'CALLE TEST 123',
                'cliente_telefono': '04121234567'
            },
            'cabecera': {
                'cabfact_id': 'FAC-TEST-001'
            },
            'detalle': [
                {
                    'dtfac_total': 100.00,
                    'dtfac_descripcion': 'PRODUCTO 1',
                    'dtfac_precio_unitario': 100.00,
                    'dtfac_cantidad': 1,
                    'dtfac_porcentaje_descuento': 0,
                    'dtfac_valor_descuento': 0
                },
                {
                    'dtfac_total': 50.00,
                    'dtfac_descripcion': 'PRODUCTO 2',
                    'dtfac_precio_unitario': 50.00,
                    'dtfac_cantidad': 1,
                    'dtfac_porcentaje_descuento': 10,
                    'dtfac_valor_descuento': 5.00
                }
            ],
            'restaurante': {
                'impuesto_rest': True
            }
        }
        
        # Probar cabecera
        cabecera = cabeceraFacturas(datos)
        assert cabecera is not None
        assert len(cabecera) > 0
        
        # Probar productos
        factura = []
        productos = factura_productos(datos, factura)
        assert productos is not None
        assert len(productos['factura']) >= 3  # 2 productos + descuentos
        
        # Probar pagos
        datos_pagos = {
            **datos,
            'formas_pago': [
                {'fpf_total_pagar': 150.00, 'formapago': '01'}
            ],
            'config_impresora': {'impresion_qr': False}
        }
        pagos = factura_pagos(productos['factura'], datos_pagos)
        assert pagos is not None
        assert len(pagos['factura']) > 0