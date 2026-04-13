# tests/test_schemas/test_factura_schema.py
"""
Pruebas para FacturaSchema
"""
import pytest
from marshmallow import ValidationError
from server.schemas.factura_schema import FacturaSchema


class TestFacturaSchema:
    """Pruebas para FacturaSchema"""
    
    @pytest.fixture
    def schema(self):
        return FacturaSchema()
    
    def test_schema_valido(self, schema, factura_valida):
        """Prueba schema con datos válidos reales"""
        resultado = schema.load(factura_valida)
        
        assert 'cabecera' in resultado
        assert 'cliente' in resultado
        assert 'detalle' in resultado
        assert 'formas_pago' in resultado
        assert 'config_impresora' in resultado
        # Verificar el total
        assert resultado['metadata']['total_factura'] == 4852.48
    
    def test_schema_sin_config_impresora(self, schema):
        """Prueba schema sin config_impresora (debe fallar)"""
        datos = {
            'cabecera_factura': {},
            'cliente': {},
            'detalle_factura': [],
            'formas_pago': []
        }
        
        with pytest.raises(ValidationError):
            schema.load(datos)
    
    def test_schema_unwrap_factura(self, schema, factura_valida):
        """Prueba que el schema extrae 'factura' correctamente"""
        resultado = schema.load(factura_valida)
        
        assert resultado is not None
        assert 'cabecera' in resultado
    
    def test_validacion_totales_inconsistentes(self, schema):
        """Prueba validación de totales inconsistentes"""
        datos = {
            'factura': {
                'config_impresora': {'impresion_qr': True, 'impresion_msgqr': True, 'impresion_cupon': False},
                'cabecera_factura': {
                    'cabfact_id': 'TEST-001',
                    'cabfact_subtotal': 100,
                    'cabfact_iva': 19,
                    'cabfact_total': 200,  # Inconsistente
                    'cabfact_tasa_conversion': 1,
                    'cabfact_fechacreacion': '2024-01-15T10:30:00'
                },
                'cliente': {
                    'cliente_documento': '9999999999999',
                    'cliente_nombres': 'TEST',
                    'cliente_apellidos': 'TEST',
                    'cliente_telefono': '123'
                },
                'detalle_factura': [
                    {
                        'detallefactura_id': 'DET-001',
                        'dtfacplu_id': 1,
                        'dtfac_cantidad': 1,
                        'dtfac_precio_unitario': 100,
                        'dtfac_iva': 19,
                        'dtfac_total': 119,
                        'dtfac_valor_descuento': 0,
                        'dtfac_porcentaje_descuento': 0,
                        'dtfac_descripcion': 'Producto',
                        'dtfac_totaldesc': 0,
                        'dtfac_ivadesc': 0
                    }
                ],
                'formas_pago': [
                    {
                        'formapago_id': '01',
                        'formapago': '01',
                        'fpf_total_pagar': 119,
                        'formapagoactura_id': 'FP-001',
                        'cfac_id': 'CFAC-001'
                    }
                ]
            }
        }
        
        with pytest.raises(ValidationError):
            schema.load(datos)