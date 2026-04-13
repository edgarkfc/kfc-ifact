# test_messages.py
"""
Script para verificar los mensajes en la base de datos
"""
import sys
sys.path.insert(0, 'C:/kfc-ifact')

from server.repositories.print_messages_repository import PrintMessagesRepository

print("=" * 60)
print("📝 VERIFICANDO MENSAJES EN BASE DE DATOS")
print("=" * 60)

repo = PrintMessagesRepository()

# Obtener todos los mensajes activos
mensajes = repo.get_all_active_ordered()

print(f"\n📋 Mensajes encontrados: {len(mensajes)}")

if mensajes:
    print("\n📄 Lista de mensajes:")
    print("-" * 40)
    for i, msg in enumerate(mensajes, 1):
        print(f"{i}. Código: {msg.get('code', 'N/A')}")
        print(f"   Contenido: {msg.get('content', 'N/A')}")
        print(f"   Orden: {msg.get('order', 0)}")
        print()
else:
    print("\n⚠️ No se encontraron mensajes activos en la tabla print_messages")
    print("\n💡 Para agregar mensajes de ejemplo, ejecuta:")
    print("""
    INSERT INTO print_messages (code, content, [order], is_active) VALUES 
    ('THANKS', '¡GRACIAS POR SU COMPRA!', 1, 1),
    ('THANKS', '¡VUELVA PRONTO!', 2, 1),
    ('PROMOTION', 'SIGUENOS EN REDES SOCIALES', 3, 1),
    ('NOTICE', 'CONSERVE SU TICKET PARA GARANTÍA', 4, 1),
    ('SPECIAL_INVOICE', 'COMPROBANTE DE PAGO VÁLIDO', 5, 1);
    """)

print("=" * 60)