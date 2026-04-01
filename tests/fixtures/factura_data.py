"""Datos de prueba para facturas"""

FACTURA_VALIDA = {
    "factura": {
        "restaurante": {
            "restaurante": "K098",
            "rest_id": 45,
            "impuesto_rest": True,
            "nro_estacion": 1
        },
        "config_impresora": {
            "impresion_qr": True,
            "impresion_msgqr": True,
            "impresion_cupon": False
        },
        "cabecera_factura": {
            "cabfact_id": "K098F000000576",
            "cabfact_nrofact_nc": None,
            "delivery_id": "PEYA-1921213682",
            "cabfact_fechacreacion": "2026-02-26T16:29:57.133",
            "cabfact_subtotal": 4183.18,  # ← Corregido: 4852.48 - 669.30 = 4183.18
            "cabfact_iva": 669.30,        # ← Corregido: 2 * 334.65 = 669.30
            "cabfact_total": 4852.48,
            "cabfact_valor_descuento": 0,
            "cabfact_porcentaje_descuento": 0,
            "cabfact_cajero": "lgarcia",
            "cabfact_tasa_conversion": 414.04
        },
        "detalle_factura": [
            {
                "detallefactura_id": "8DBF8DE7-5113-F111-ADF8-D0C1B5009507",
                "dtfacplu_id": 4178,
                "dtfac_cantidad": 2,
                "dtfac_precio_unitario": 2426.24,
                "dtfac_iva": 334.65,
                "dtfac_total": 4852.48,
                "aplicaImpuesto1": 1,
                "aplicaImpuesto2": 0,
                "aplicaImpuesto3": 0,
                "aplicaImpuesto4": 0,
                "aplicaImpuesto5": 0,
                "dtfac_valor_descuento": 0,
                "dtfac_porcentaje_descuento": 0,
                "dtfac_totaldesc": 0,
                "dtfac_ivadesc": 0,
                "dtfac_descripcion": "COMBO 2PZ CON PAPAS"
            }
        ],
        "cliente": {
            "cliente_id": "C62EB822-216B-497A-8F61-AA1F2DD3945C",
            "cliente_documento": "V20289719",
            "cliente_nombres": "ALEJANDRO",
            "cliente_apellidos": "",
            "cliente_telefono": "04241572784",
            "cliente_direccion": "",
            "cliente_email": "AAA@INBOX.COM"
        },
        "formas_pago": [
            {
                "formapagoactura_id": "8FBF8DE7-5113-F111-ADF8-D0C1B5009507",
                "formapago_id": "5917064E-A357-EC11-94F6-0050F2D50918",
                "fpf_total_pagar": 4852.48,
                "formapago": "01"
            }
        ]
    }
}

# Factura con múltiples productos y descuentos
FACTURA_VALIDA_MULTIPLE = {
    "factura": {
        "restaurante": {
            "restaurante": "K098",
            "rest_id": 45,
            "impuesto_rest": True,
            "nro_estacion": 1
        },
        "config_impresora": {
            "impresion_qr": True,
            "impresion_msgqr": False,
            "impresion_cupon": True
        },
        "cabecera_factura": {
            "cabfact_id": "K098F000000577",
            "cabfact_nrofact_nc": None,
            "delivery_id": "TEST-123",
            "cabfact_fechacreacion": "2026-03-31T16:00:00",
            "cabfact_subtotal": 1000.00,
            "cabfact_iva": 160.00,
            "cabfact_total": 1160.00,
            "cabfact_valor_descuento": 0,
            "cabfact_porcentaje_descuento": 0,
            "cabfact_cajero": "test",
            "cabfact_tasa_conversion": 1.00
        },
        "detalle_factura": [
            {
                "detallefactura_id": "TEST-001",
                "dtfacplu_id": 1,
                "dtfac_cantidad": 2,
                "dtfac_precio_unitario": 500.00,
                "dtfac_iva": 80.00,
                "dtfac_total": 1000.00,
                "aplicaImpuesto1": 1,
                "aplicaImpuesto2": 0,
                "aplicaImpuesto3": 0,
                "aplicaImpuesto4": 0,
                "aplicaImpuesto5": 0,
                "dtfac_valor_descuento": 0,
                "dtfac_porcentaje_descuento": 0,
                "dtfac_totaldesc": 0,
                "dtfac_ivadesc": 0,
                "dtfac_descripcion": "PRODUCTO TEST"
            },
            {
                "detallefactura_id": "TEST-002",
                "dtfacplu_id": 2,
                "dtfac_cantidad": 1,
                "dtfac_precio_unitario": 0,
                "dtfac_iva": 0,
                "dtfac_total": 0,
                "aplicaImpuesto1": 0,
                "aplicaImpuesto2": 0,
                "aplicaImpuesto3": 0,
                "aplicaImpuesto4": 0,
                "aplicaImpuesto5": 0,
                "dtfac_valor_descuento": 0,
                "dtfac_porcentaje_descuento": 0,
                "dtfac_totaldesc": 0,
                "dtfac_ivadesc": 0,
                "dtfac_descripcion": "PRODUCTO COMPLEMENTARIO"
            }
        ],
        "cliente": {
            "cliente_id": "TEST-CLIENT-001",
            "cliente_documento": "V12345678",
            "cliente_nombres": "TEST",
            "cliente_apellidos": "USER",
            "cliente_telefono": "04121234567",
            "cliente_direccion": "Calle Test",
            "cliente_email": "test@test.com"
        },
        "formas_pago": [
            {
                "formapagoactura_id": "TEST-PAY-001",
                "formapago_id": "PAY-001",
                "fpf_total_pagar": 1160.00,
                "formapago": "01"
            }
        ]
    }
}

FACTURA_INVALIDA = {
    "factura": {
        "restaurante": {
            "restaurante": "K098",
            "rest_id": 45,
            "impuesto_rest": True,
            "nro_estacion": 1
        },
        "config_impresora": {
            "impresion_qr": True,
            "impresion_msgqr": True,
            "impresion_cupon": False
        },
        "cabecera_factura": {
            "cabfact_id": "K098F000000576",
            "cabfact_nrofact_nc": None,
            "delivery_id": "PEYA-1921213682",
            "cabfact_fechacreacion": "2026-02-26T16:29:57.133",
            "cabfact_subtotal": 4083.1724,  # ← Valor incorrecto a propósito
            "cabfact_iva": 669.31,          # ← Valor incorrecto a propósito
            "cabfact_total": 4852.48,
            "cabfact_valor_descuento": 0,
            "cabfact_porcentaje_descuento": 0,
            "cabfact_cajero": "lgarcia",
            "cabfact_tasa_conversion": 414.04
        },
        "detalle_factura": [
            {
                "detallefactura_id": "8DBF8DE7-5113-F111-ADF8-D0C1B5009507",
                "dtfacplu_id": 4178,
                "dtfac_cantidad": 2,
                "dtfac_precio_unitario": 2426.24,
                "dtfac_iva": 334.65,
                "dtfac_total": 4852.48,
                "aplicaImpuesto1": 1,
                "aplicaImpuesto2": 0,
                "aplicaImpuesto3": 0,
                "aplicaImpuesto4": 0,
                "aplicaImpuesto5": 0,
                "dtfac_valor_descuento": 0,
                "dtfac_porcentaje_descuento": 0,
                "dtfac_totaldesc": 0,
                "dtfac_ivadesc": 0,
                "dtfac_descripcion": "COMBO 2PZ CON PAPAS"
            }
        ],
        "cliente": {
            "cliente_id": "C62EB822-216B-497A-8F61-AA1F2DD3945C",
            "cliente_documento": "V20289719",
            "cliente_nombres": "ALEJANDRO",
            "cliente_apellidos": "",
            "cliente_telefono": "04241572784",
            "cliente_direccion": "",
            "cliente_email": "AAA@INBOX.COM"
        },
        "formas_pago": [
            {
                "formapagoactura_id": "8FBF8DE7-5113-F111-ADF8-D0C1B5009507",
                "formapago_id": "5917064E-A357-EC11-94F6-0050F2D50918",
                "fpf_total_pagar": 4852.48,
                "formapago": "01"
            }
        ]
    }
}

FACTURA_DIFERENCIA_TOTALES = FACTURA_INVALIDA  # Misma que inválida por la diferencia