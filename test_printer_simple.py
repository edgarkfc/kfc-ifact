# test_printer_simple.py
"""
Prueba básica de comunicación con la impresora fiscal
Ejecutar con: python test_printer_simple.py
"""
import sys
from pathlib import Path

# Agregar el proyecto al path
sys.path.insert(0, str(Path(__file__).parent))

from server.printer.fiscal import Tfhka


def probar_impresora():
    """Prueba básica de comandos"""
    
    print("=" * 60)
    print("🖨️ PRUEBA DE IMPRESORA FISCAL")
    print("=" * 60)
    
    # Configurar puerto
    puerto = input("\n📌 Puerto COM (ej: COM3): ").strip() or "COM3"
    
    # Crear instancia
    printer = Tfhka()
    printer.Port.portName = puerto
    
    # Conectar
    print(f"\n🔌 Conectando a impresora en {puerto}...")
    try:
        if not printer.OpenFpctrl(puerto):
            print("❌ Error de conexión")
            print("\nVerifique:")
            print("   1. La impresora está encendida")
            print("   2. El cable USB está conectado")
            print("   3. El puerto COM es correcto")
            return
    except Exception as e:
        print(f"❌ Excepción al conectar: {e}")
        return
    
    print("✅ Conectado exitosamente")
    
    # Obtener estado
    print("\n📊 Leyendo estado...")
    try:
        estado = printer.ReadFpStatus()
        print(f"   Estado: {estado}")
    except Exception as e:
        print(f"   Error leyendo estado: {e}")
    
    # Preguntar si quiere imprimir
    print("\n" + "=" * 60)
    imprimir = input("¿Desea imprimir una prueba? (s/n): ").strip().lower()
    
    if imprimir == 's':
        print("\n🖨️ Imprimiendo...")
        
        # Comandos de prueba para impresora fiscal
        comandos = [
            "iS* CONSUMIDOR FINAL",
            "iR* 9999999",
            "i03Direccion: AV. PRINCIPAL 123",
            "i04Telefono: 0999999999",
            "i05Transaccion: TEST-PRINTER-001",
            "!0000010000000010001X PRODUCTO DE PRUEBA",
            "3",
            "20100000000100",
        ]
        
        for cmd in comandos:
            print(f"   → {cmd[:50]}...")
            try:
                printer.SendCmd(cmd)
            except Exception as e:
                print(f"      ❌ Error: {e}")
        
        print("✅ Impresión completada")
    else:
        print("❌ Impresión cancelada")
    
    # Cerrar conexión
    print("\n🔌 Desconectando...")
    try:
        printer.CloseFpctrl()
        print("✅ Desconectado")
    except Exception as e:
        print(f"❌ Error al desconectar: {e}")
    
    print("\n" + "=" * 60)
    print("✅ Prueba completada")
    print("=" * 60)


if __name__ == "__main__":
    probar_impresora()