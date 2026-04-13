# test_qr_fix.py
"""
Script para probar la generación de QR después del cambio
Ubicación: C:\kfc-ifact\test_qr_fix.py
"""
import sys
import os

# Agregar el directorio del proyecto al path
sys.path.insert(0, 'C:/kfc-ifact')

# Configurar logging para ver detalles
import logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

print("=" * 60)
print("🔧 PROBANDO QR SERVICE")
print("=" * 60)

try:
    from server.services.qr_service import QRService
    print("\n✅ QRService importado correctamente")
except Exception as e:
    print(f"\n❌ Error importando QRService: {e}")
    sys.exit(1)

# Instanciar QRService
qr = QRService()
print(f"\n📦 QRService instanciado: {qr}")

# ============================================
# PRUEBA 1: Validar impresión QR
# ============================================
print("\n" + "=" * 60)
print("PRUEBA 1: Validar impresión QR")
print("=" * 60)

config_true = {'impresion_qr': True}
config_false = {'impresion_qr': False}
config_vacio = {}

print(f"\n📋 Config con True: {config_true}")
print(f"   Resultado: {qr.validar_impresion_qr(config_true)}")

print(f"\n📋 Config con False: {config_false}")
print(f"   Resultado: {qr.validar_impresion_qr(config_false)}")

print(f"\n📋 Config vacía: {config_vacio}")
print(f"   Resultado: {qr.validar_impresion_qr(config_vacio)}")

# ============================================
# PRUEBA 2: Generar trama numérica
# ============================================
print("\n" + "=" * 60)
print("PRUEBA 2: Generar trama numérica (procesar_qr)")
print("=" * 60)

try:
    from server.controllers.helpers.algortimoqr import procesar_qr
    print("\n✅ Algoritmo QR importado")
    
    trama_numerica = procesar_qr()
    print(f"\n🔢 Trama numérica generada: {trama_numerica}")
    
    if trama_numerica:
        print(f"   ✅ Éxito: {trama_numerica}")
        print(f"   Tipo: {type(trama_numerica)}")
        print(f"   Longitud: {len(str(trama_numerica))}")
    else:
        print(f"   ❌ Falló: trama_numerica es {trama_numerica}")
        
except Exception as e:
    print(f"\n❌ Error en procesar_qr: {e}")
    import traceback
    traceback.print_exc()
    trama_numerica = None

# ============================================
# PRUEBA 3: Generar trama completa (con prefijo)
# ============================================
print("\n" + "=" * 60)
print("PRUEBA 3: Generar trama completa (QRService)")
print("=" * 60)

try:
    trama_completa = qr.generar_trama_completa()
    print(f"\n🔢 Trama completa generada: {trama_completa}")
    
    if trama_completa:
        print(f"   ✅ Éxito: '{trama_completa}'")
        print(f"   Prefijo: '{trama_completa[0]}'")
        print(f"   Número: '{trama_completa[1:]}'")
        print(f"   Longitud total: {len(trama_completa)}")
    else:
        print(f"   ❌ Falló: trama_completa es {trama_completa}")
        
except Exception as e:
    print(f"\n❌ Error en generar_trama_completa: {e}")
    import traceback
    traceback.print_exc()

# ============================================
# PRUEBA 4: Probar el método procesar_qr del servicio
# ============================================
print("\n" + "=" * 60)
print("PRUEBA 4: Procesar QR completo (QRService.procesar_qr)")
print("=" * 60)

try:
    datos_prueba = {
        'config_impresora': {'impresion_qr': True},
        'cabecera': {'cabfact_id': 'TEST-001'}
    }
    
    resultado = qr.procesar_qr(datos_prueba)
    print(f"\n📋 Resultado: {resultado}")
    
    if resultado and resultado.get('success') and resultado.get('habilitado'):
        print(f"\n   ✅ QR generado exitosamente:")
        print(f"      qr_texto: {resultado.get('qr_texto')}")
        print(f"      qr_trama_numerica: {resultado.get('qr_trama_numerica')}")
        print(f"      qr_prefijo: {resultado.get('qr_prefijo')}")
    elif resultado:
        print(f"\n   ⚠️ QR no habilitado: {resultado.get('message')}")
    else:
        print(f"\n   ❌ Error: resultado es None")
        
except Exception as e:
    print(f"\n❌ Error en procesar_qr: {e}")
    import traceback
    traceback.print_exc()

# ============================================
# RESUMEN FINAL
# ============================================
print("\n" + "=" * 60)
print("📊 RESUMEN FINAL")
print("=" * 60)

if trama_completa:
    print("\n✅ QR FUNCIONA CORRECTAMENTE")
    print(f"   Trama de ejemplo: {trama_completa}")
else:
    print("\n❌ QR NO FUNCIONA")
    print("\n🔧 Posibles causas:")
    print("   1. Base de datos no tiene datos en tabla pivotqrs")
    print("   2. Error de conexión a SQL Server")
    print("   3. El algoritmo procesar_qr() está fallando")
    print("\n💡 Para verificar la BD, ejecuta:")
    print("   python -c \"from server.config.database import db; print(db.execute_query('SELECT * FROM pivotqrs', fetch=True))\"")

print("\n" + "=" * 60)