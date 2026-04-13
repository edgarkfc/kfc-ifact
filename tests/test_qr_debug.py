# test_qr_debug.py
"""
Script para depurar la generación del QR
"""
from server.controllers.helpers.algortimoqr import procesar_qr
from server.services.qr_service import QRService

print("=" * 50)
print("🔍 DEPURANDO GENERACIÓN QR")
print("=" * 50)

# Probar directamente el algoritmo
print("\n1. Probando procesar_qr() directamente:")
try:
    resultado = procesar_qr()
    print(f"   Resultado: {resultado}")
    print(f"   Tipo: {type(resultado)}")
except Exception as e:
    print(f"   Error: {e}")
    import traceback
    traceback.print_exc()

# Probar con QRService
print("\n2. Probando QRService.generar_trama_completa():")
try:
    qr_service = QRService()
    trama = qr_service.generar_trama_completa()
    print(f"   Resultado: {trama}")
    print(f"   Tipo: {type(trama)}")
except Exception as e:
    print(f"   Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 50)