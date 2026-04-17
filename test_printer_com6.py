# test_printer_com6.py
"""
Prueba con puerto COM6 (Prolific USB-to-Serial Comm Port)
Ejecutar con: python test_printer_com6.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from server.printer.fiscal import Tfhka


def probar_impresora():
    """Prueba con puerto COM6"""
    
    print("=" * 60)
    print("🖨️ PRUEBA DE IMPRESORA FISCAL - COM6")
    print("=" * 60)
    
    puerto = "COM6"
    
    print(f"\n🔌 Conectando a impresora en {puerto}...")
    
    printer = Tfhka()
    printer.Port.portName = puerto
    
    try:
        if not printer.OpenFpctrl(puerto):
            print(f"❌ Error de conexión a {puerto}")
            print("\nVerifique:")
            print("   1. La impresora está encendida")
            print("   2. El cable USB está conectado")
            print("   3. No hay otra aplicación usando el puerto")
            return
    except Exception as e:
        print(f"❌ Excepción al conectar: {e}")
        return
    
    print("✅ Conectado exitosamente")
    
    # Obtener estado
    print("\n📊 Leyendo estado de la impresora...")
    try:
        estado = printer.ReadFpStatus()
        print(f"   Estado: {estado}")
    except Exception as e:
        print(f"   Error leyendo estado: {e}")
    
    # Preguntar si quiere imprimir
    print("\n" + "=" * 60)
    imprimir = input("¿Desea imprimir una prueba? (s/n): ").strip().lower()
    
    if imprimir == 's':
        print("\n🖨️ Enviando comandos a la impresora...")
        print("-" * 40)
        
        # Comandos de prueba para impresora fiscal
        comandos = [
            "iS* CONSUMIDOR FINAL",
            "iR* 9999999",
            "i03Direccion: AV. PRINCIPAL 123",
            "i04Telefono: 0999999999",
            "i05Transaccion: TEST-COM6-001",
            "!0000010000000010001X PRODUCTO DE PRUEBA",
            "3",
            "20100000000100",
        ]
        
        for i, cmd in enumerate(comandos, 1):
            print(f"   {i}. {cmd[:50]}...")
            try:
                resultado = printer.SendCmd(cmd)
                if not resultado:
                    print("      ⚠️ Comando falló")
            except Exception as e:
                print(f"      ❌ Error: {e}")
        
        print("-" * 40)
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