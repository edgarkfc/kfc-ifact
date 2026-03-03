# C:\kfc-ifact\check_full_structure.py
import sys
import os

print("=" * 60)
print("VERIFICACIÓN COMPLETA DEL PROYECTO")
print("=" * 60)

project_root = os.getcwd()
print(f"\n📁 Directorio raíz: {project_root}")

# Agregar al path
sys.path.insert(0, project_root)

print("\n📌 Python PATH:")
for i, p in enumerate(sys.path[:5], 1):
    print(f"  {i}. {p}")

print("\n📂 Estructura de archivos:")

def check_file(path, description):
    full_path = os.path.join(project_root, path)
    exists = os.path.exists(full_path)
    status = "✅" if exists else "❌"
    print(f"  {status} {description}: {path}")
    return exists

print("\nArchivos principales:")
check_file("server/app.py", "App principal")
check_file("server/routes/api.py", "API routes")
check_file("server/controllers/bills_controller.py", "Bills controller")
check_file("server/controllers/helpers/validators.py", "Validators")
check_file("server/controllers/helpers/cabecera_factura.py", "Cabecera factura")
check_file("tests/conftest.py", "Pytest conftest")
check_file("tests/test_routes.py", "Test routes")

print("\n🔄 Verificando importaciones:")

# 1. Verificar importación de routes
try:
    print("\n  Intentando: from server.routes.api import facturas_bp")
    from server.routes.api import facturas_bp
    print("  ✅ ¡Éxito! facturas_bp importado correctamente")
except Exception as e:
    print(f"  ❌ Error: {type(e).__name__}: {e}")

# 2. Verificar importación de controllers
try:
    print("\n  Intentando: from server.controllers.bills_controller import armar_factura")
    from server.controllers.bills_controller import armar_factura
    print("  ✅ ¡Éxito! armar_factura importado correctamente")
except Exception as e:
    print(f"  ❌ Error: {type(e).__name__}: {e}")

# 3. Verificar importación de validators
try:
    print("\n  Intentando: from server.controllers.helpers.validators import FacturaSchema")
    from server.controllers.helpers.validators import FacturaSchema
    print("  ✅ ¡Éxito! FacturaSchema importado correctamente")
except Exception as e:
    print(f"  ❌ Error: {type(e).__name__}: {e}")

print("\n" + "=" * 60)