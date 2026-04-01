import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from marshmallow import ValidationError
from server.controllers.helpers.validators import (
    FacturaSchema,
    FormaPagoSchema,
    DetalleFacturaSchema,
    ClienteSchema,
    CabeceraFacturaSchema,
    ConfigImpresoraSchema
)

class TestValidators:
    """Tests para los validadores Marshmallow"""
    
    def test_factura_schema_valida(self, factura_valida_data):
        """Test factura válida pasa validación"""
        schema = FacturaSchema()
        
        # Extraer factura del wrapper si existe
        if 'factura' in factura_valida_data:
            datos = factura_valida_data['factura']
        else:
            datos = factura_valida_data
        
        resultado = schema.load(datos)
        
        assert resultado is not None
        # El schema transforma los nombres
        assert 'cliente' in resultado
        assert 'cabecera' in resultado  # ← Cambiado de cabecera_factura a cabecera
        assert 'detalle' in resultado   # ← Cambiado de detalle_factura a detalle
        
        # Verificar que los totales sean correctos
        cabecera = resultado['cabecera']
        total_cabecera = cabecera.get('cabfact_total', 0)
        subtotal_cabecera = cabecera.get('cabfact_subtotal', 0)
        iva_cabecera = cabecera.get('cabfact_iva', 0)
        
        # Verificar relación: total = subtotal + iva
        assert abs((subtotal_cabecera + iva_cabecera) - total_cabecera) <= 0.05
    
    def test_factura_schema_invalida(self, factura_invalida_data):
        """Test factura inválida lanza ValidationError"""
        schema = FacturaSchema()
        
        if 'factura' in factura_invalida_data:
            datos = factura_invalida_data['factura']
        else:
            datos = factura_invalida_data
        
        with pytest.raises(ValidationError) as exc_info:
            schema.load(datos)
        
        assert 'cabecera_factura' in exc_info.value.messages
    
    def test_forma_pago_valida(self):
        """Test forma de pago válida"""
        schema = FormaPagoSchema()
        datos = {
            "formapago_id": "123",
            "fpf_total_pagar": 100.50,
            "formapago": "01"
        }
        
        resultado = schema.load(datos)
        assert resultado['fpf_total_pagar'] == 100.50
    
    @pytest.mark.parametrize("formapago,expected_error", [
        ("1", "exactamente 2 dígitos"),
        ("abc", "2 dígitos numéricos"),
        ("99", "Metodo de pago no registrado"),
        ("00", "Metodo de pago no registrado"),
    ])
    def test_forma_pago_invalida(self, formapago, expected_error):
        """Test formas de pago inválidas"""
        schema = FormaPagoSchema()
        datos = {
            "formapago_id": "123",
            "fpf_total_pagar": 100.50,
            "formapago": formapago
        }
        
        with pytest.raises(ValidationError) as exc_info:
            schema.load(datos)
        
        error_msg = str(exc_info.value.messages)
        assert expected_error in error_msg or 'formapago' in exc_info.value.messages
    
    def test_detalle_factura_valido(self):
        """Test detalle factura válido"""
        schema = DetalleFacturaSchema()
        datos = {
            "detallefactura_id": "123",
            "dtfacplu_id": 1,
            "dtfac_cantidad": 2,
            "dtfac_precio_unitario": 100.00,
            "dtfac_iva": 16.00,
            "dtfac_total": 200.00,
            "dtfac_valor_descuento": 0,
            "dtfac_porcentaje_descuento": 0,
            "dtfac_descripcion": "Producto test"
        }
        
        resultado = schema.load(datos)
        assert resultado['dtfac_cantidad'] == 2
    
    def test_detalle_factura_con_descuento(self):
        """Test detalle factura con descuento válido"""
        schema = DetalleFacturaSchema()
        datos = {
            "detallefactura_id": "123",
            "dtfacplu_id": 1,
            "dtfac_cantidad": 2,
            "dtfac_precio_unitario": 100.00,
            "dtfac_iva": 16.00,
            "dtfac_total": 180.00,  # 200 - 20 de descuento
            "dtfac_valor_descuento": 20.00,
            "dtfac_porcentaje_descuento": 10,
            "dtfac_descripcion": "Producto test"
        }
        
        resultado = schema.load(datos)
        assert resultado['dtfac_valor_descuento'] == 20.00
    
    def test_cliente_valido(self):
        """Test cliente válido"""
        schema = ClienteSchema()
        datos = {
            "cliente_documento": "V12345678",
            "cliente_nombres": "Juan",
            "cliente_telefono": "04121234567",
            "cliente_direccion": "Calle test"
        }
        
        resultado = schema.load(datos)
        assert resultado['cliente_nombres'] == "Juan"
    
    def test_cliente_direccion_null(self):
        """Test cliente con dirección null"""
        schema = ClienteSchema()
        datos = {
            "cliente_documento": "V12345678",
            "cliente_nombres": "Juan",
            "cliente_telefono": "04121234567",
            "cliente_direccion": None
        }
        
        resultado = schema.load(datos)
        assert resultado['cliente_direccion'] is None
    
    def test_cabecera_factura_valida(self):
        """Test cabecera factura válida"""
        schema = CabeceraFacturaSchema()
        datos = {
            "cabfact_id": "FAC001",
            "cabfact_fechacreacion": "2026-03-31T10:00:00",
            "cabfact_subtotal": 1000.00,
            "cabfact_iva": 160.00,
            "cabfact_total": 1160.00,
            "cabfact_tasa_conversion": 1.00
        }
        
        resultado = schema.load(datos)
        assert resultado['cabfact_subtotal'] == 1000.00
    
    def test_cabecera_factura_con_descuento(self):
        """Test cabecera factura con descuento"""
        schema = CabeceraFacturaSchema()
        datos = {
            "cabfact_id": "FAC001",
            "cabfact_fechacreacion": "2026-03-31T10:00:00",
            "cabfact_subtotal": 1000.00,
            "cabfact_iva": 160.00,
            "cabfact_total": 1060.00,  # 1160 - 100 descuento
            "cabfact_valor_descuento": 100.00,
            "cabfact_tasa_conversion": 1.00
        }
        
        resultado = schema.load(datos)
        assert resultado['cabfact_valor_descuento'] == 100.00
    
    def test_config_impresora_valida(self):
        """Test configuración impresora válida"""
        schema = ConfigImpresoraSchema()
        datos = {
            "impresion_qr": True,
            "impresion_msgqr": False,
            "impresion_cupon": True
        }
        
        resultado = schema.load(datos)
        assert resultado['impresion_qr'] is True
        assert resultado['impresion_msgqr'] is False