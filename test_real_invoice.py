# test_real_invoice.py
"""
Prueba de impresión con factura real
"""
import sys
from pathlib import Path

from sqlalchemy import null

sys.path.insert(0, str(Path(__file__).parent))

from server.printer.fiscal import Tfhka
from server.services.qr_service import QRService
from server.controllers.helpers.create_invoice import (
    cabeceraFacturas,
    factura_productos,
    factura_pagos
)


def procesar_y_imprimir_factura(datos_json):
    """Procesa el JSON y envía a la impresora"""
    
    print("=" * 60)
    print("🖨️ PROCESANDO FACTURA REAL")
    print("=" * 60)
    
    # Extraer datos
    factura_data = datos_json['factura']
    config_impresora = factura_data.get('config_impresora', {})
    cabecera = factura_data.get('cabecera_factura', {})
    cliente = factura_data.get('cliente', {})
    detalle = factura_data.get('detalle_factura', [])
    formas_pago = factura_data.get('formas_pago', [])
    
    # Generar líneas de factura
    lineas = []
    
    # 1. Cabecera
    print("\n📋 Generando cabecera...")
    cabecera_lines = cabeceraFacturas({
        'cliente': cliente,
        'cabecera': cabecera
    })
    lineas.extend(cabecera_lines)
    print(f"   {len(cabecera_lines)} líneas de cabecera")
    
    # 2. Productos
    print("\n📦 Procesando productos...")
    productos_result = factura_productos({
        'detalle': detalle,
        'restaurante': factura_data.get('restaurante', {})
    }, [])
    lineas.extend(productos_result['factura'])
    print(f"   {len(detalle)} productos procesados")
    
    # 3. Separador
    lineas.append("---")
    
    # 4. QR
    if config_impresora.get('impresion_qr', False):
        print("\n🔢 Generando QR...")
        qr_service = QRService()
        trama_qr = qr_service.generar_trama_completa()
        if trama_qr:
            lineas.append(trama_qr)
            print(f"   QR: {trama_qr}")
    
    # 5. Pagos y descuentos
    print("\n💰 Procesando pagos...")
    pagos_result = factura_pagos([], {
        'cabecera': cabecera,
        'formas_pago': formas_pago,
        'config_impresora': config_impresora
    })
    lineas.extend(pagos_result['factura'])
    print(f"   {len(formas_pago)} formas de pago")
    
    # Mostrar líneas a imprimir
    print("\n" + "=" * 60)
    print("📄 LÍNEAS A IMPRIMIR:")
    print("=" * 60)
    for i, linea in enumerate(lineas, 1):
        print(f"{i:3d}. {linea[:70]}{'...' if len(linea) > 70 else ''}")
    
    # Conectar a impresora
    print("\n" + "=" * 60)
    print("🖨️ ENVIANDO A IMPRESORA")
    print("=" * 60)
    
    puerto = "COM6"
    printer = Tfhka()
    printer.Port.portName = puerto
    
    print(f"\n🔌 Conectando a {puerto}...")
    if not printer.OpenFpctrl(puerto):
        print("❌ Error de conexión")
        return
    
    print("✅ Conectado")
    
    # Enviar líneas
    print("\n📤 Enviando comandos...")
    exito = 0
    fallo = 0
    
    for i, linea in enumerate(lineas, 1):
        if linea and linea.strip():
            cmd = linea.strip()
            print(f"   {i:3d}. {cmd[:50]}...", end=" ")
            try:
                resultado = printer.SendCmd(cmd)
                if resultado:
                    print("✅")
                    exito += 1
                else:
                    print("❌")
                    fallo += 1
            except Exception as e:
                print(f"❌ {str(e)[:30]}")
                fallo += 1
    
    # Cerrar conexión
    printer.CloseFpctrl()
    
    print("\n" + "=" * 60)
    print(f"📊 RESULTADO: {exito} éxitos, {fallo} fallos")
    print("✅ Proceso completado")
    print("=" * 60)


if __name__ == "__main__":
    # Tu JSON
    factura_json = {
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
            "impresion_cupon": True
            },
            "cabecera_factura": {
            "cabfact_id": "K098F000000576",
            "cabfact_nrofact_nc": "0000",
            "delivery_id": "PEYA-1921213682",
            "cabfact_fechacreacion": "2026-02-26T16:29:57.133",
            "cabfact_subtotal": 4183.1724,
            "cabfact_iva": 669.31,
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
                "dtfac_totaldesc":0,
                "dtfac_ivadesc": 0,
                "dtfac_descripcion": "COMBO 2PZ CON PAPAS"
            },
            {
                "detallefactura_id": "8CBF8DE7-5113-F111-ADF8-D0C1B5009507",        
                "dtfacplu_id": 258,
                "dtfac_cantidad": 1,
                "dtfac_precio_unitario": 0,
                "dtfac_iva": 0,
                "dtfac_total": 0,
                "aplicaImpuesto1": 1,
                "aplicaImpuesto2": 0,
                "aplicaImpuesto3": 0,
                "aplicaImpuesto4": 0,
                "aplicaImpuesto5": 0,
                "dtfac_valor_descuento": 0,
                "dtfac_porcentaje_descuento": 0,
                "dtfac_totaldesc": 0,
                "dtfac_ivadesc": 0,
                "dtfac_descripcion": ".No"        
            },
            {
                "detallefactura_id": "8BBF8DE7-5113-F111-ADF8-D0C1B5009507",       
                "dtfacplu_id": 246,
                "dtfac_cantidad": 1,
                "dtfac_precio_unitario": 0,
                "dtfac_iva": 0,
                "dtfac_total": 0,
                "aplicaImpuesto1": 1,
                "aplicaImpuesto2": 0,
                "aplicaImpuesto3": 0,
                "aplicaImpuesto4": 0,
                "aplicaImpuesto5": 0,
                "dtfac_valor_descuento": 0,
                "dtfac_porcentaje_descuento": 0,
                "dtfac_totaldesc": 0,
                "dtfac_ivadesc": 0,
                "dtfac_descripcion": "..KOLITA"        
            }
            ],
            "cliente": {
            "cliente_id": "C62EB822-216B-497A-8F61-AA1F2DD3945C",
            "cliente_documento": "V20289719",
            "cliente_nombres": "ALEJANDRO",
            "cliente_apellidos": null,
            "cliente_telefono": "04241572784",
            "cliente_direccion": "NULL",
            "cliente_email": "AAA@INBOX.COM"
            },
            "formas_pago": [
            {
                "formapagoactura_id": "8FBF8DE7-5113-F111-ADF8-D0C1B5009507",
                "formapago_id": "5917064E-A357-EC11-94F6-0050F2D50918",
                "fpf_total_pagar": 4552.48,
                "formapago": "16"
            },
            {
                "formapagoactura_id": "8FBF8DE7-5113-F111-ADF8-D0C1B5009507",
                "formapago_id": "5917064E-A357-EC11-94F6-0050F2D50918",
                "fpf_total_pagar": 300.00,
                "formapago": "01"
            }
            ]
        }
    }
    
    procesar_y_imprimir_factura(factura_json)