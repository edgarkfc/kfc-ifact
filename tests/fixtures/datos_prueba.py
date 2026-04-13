# tests/fixtures/datos_prueba.py
"""
Datos de prueba para tests
"""

FACTURA_BASE = {
    "factura": {
        "config_impresora": {
            "impresion_qr": True,
            "impresion_msgqr": True,
            "impresion_cupon": False
        },
        "cabecera_factura": {
            "cabfact_id": "TEST-001",
            "cabfact_subtotal": 100.00,
            "cabfact_iva": 19.00,
            "cabfact_total": 119.00,
            "cabfact_tasa_conversion": 1,
            "cabfact_fechacreacion": "2024-01-15 10:30:00"
        },
        "cliente": {
            "cliente_documento": "9999999999999",
            "cliente_nombres": "CONSUMIDOR FINAL",
            "cliente_telefono": "000000000",
            "cliente_direccion": ""
        },
        "detalle_factura": [],
        "formas_pago": [
            {
                "formapago_id": "01",
                "formapago": "01",
                "fpf_total_pagar": 119.00
            }
        ]
    }
}

FACTURA_CON_PRODUCTOS = {
    "factura": {
        "config_impresora": {
            "impresion_qr": True,
            "impresion_msgqr": True,
            "impresion_cupon": False
        },
        "cabecera_factura": {
            "cabfact_id": "TEST-002",
            "cabfact_subtotal": 1000.00,
            "cabfact_iva": 190.00,
            "cabfact_total": 1190.00,
            "cabfact_tasa_conversion": 1
        },
        "cliente": {
            "cliente_documento": "20123456789",
            "cliente_nombres": "EMPRESA TEST",
            "cliente_telefono": "0999999999",
            "cliente_direccion": "Av. Principal 123"
        },
        "detalle_factura": [
            {
                "detallefactura_id": "DET-001",
                "dtfacplu_id": 123,
                "dtfac_cantidad": 1,
                "dtfac_precio_unitario": 1000.00,
                "dtfac_iva": 190.00,
                "dtfac_total": 1000.00,
                "dtfac_valor_descuento": 0,
                "dtfac_porcentaje_descuento": 0,
                "dtfac_descripcion": "Laptop HP"
            }
        ],
        "formas_pago": [
            {
                "formapago_id": "01",
                "formapago": "01",
                "fpf_total_pagar": 1190.00
            }
        ]
    }
}

FACTURA_CON_DESCUENTO = {
    "factura": {
        "config_impresora": {
            "impresion_qr": True,
            "impresion_msgqr": True,
            "impresion_cupon": False
        },
        "cabecera_factura": {
            "cabfact_id": "TEST-003",
            "cabfact_subtotal": 900.00,
            "cabfact_iva": 171.00,
            "cabfact_total": 1071.00,
            "cabfact_valor_descuento": 100.00,
            "cabfact_porcentaje_descuento": 10,
            "cabfact_tasa_conversion": 1
        },
        "cliente": {
            "cliente_documento": "20123456789",
            "cliente_nombres": "EMPRESA TEST",
            "cliente_telefono": "0999999999"
        },
        "detalle_factura": [
            {
                "detallefactura_id": "DET-001",
                "dtfacplu_id": 123,
                "dtfac_cantidad": 1,
                "dtfac_precio_unitario": 1000.00,
                "dtfac_iva": 190.00,
                "dtfac_total": 1000.00,
                "dtfac_valor_descuento": 100,
                "dtfac_porcentaje_descuento": 10,
                "dtfac_descripcion": "Laptop HP con descuento"
            }
        ],
        "formas_pago": [
            {
                "formapago_id": "01",
                "formapago": "01",
                "fpf_total_pagar": 1071.00
            }
        ]
    }
}

NOTA_CREDITO_BASE = {
    "nota_credito": {
        "config_impresora": {
            "impresion_qr": False,
            "impresion_msgqr": True,
            "impresion_cupon": False
        },
        "cabecera_factura": {
            "cabfact_id": "NC-001",
            "cabfact_subtotal": 50.00,
            "cabfact_iva": 9.50,
            "cabfact_total": 59.50,
            "cabfact_tasa_conversion": 1
        },
        "cliente": {
            "cliente_documento": "9999999999999",
            "cliente_nombres": "CONSUMIDOR FINAL",
            "cliente_telefono": "000000000"
        },
        "detalle_factura": [],
        "formas_pago": []
    }
}