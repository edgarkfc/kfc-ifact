# check_imports.py
import sys
import os

print("=" * 50)
print("VERIFICANDO IMPORTACIONES")
print("=" * 50)

project_root = os.getcwd()
print(f"Directorio actual: {project_root}")

# Agregar al path
sys.path.insert(0, project_root)

print("\nPython path:")
for i, path in enumerate(sys.path[:5], 1):
    print(f"  {i}. {path}")

print("\nProbando importaciones:")
try:
    from server.routes.api import facturas_bp
    print("✓ from server.routes.api import facturas_bp")
except Exception as e:
    print(f"✗ Error: {e}")

try:
    from server.controllers.bills_controller import armar_factura
    print("✓ from controllers.bills_controller import armar_factura")
except Exception as e:
    print(f"✗ Error: {e}")

try:
    from server.controllers.helpers.validators import FacturaSchema
    print("✓ from controllers.helpers.validators import FacturaSchema")
except Exception as e:
    print(f"✗ Error: {e}")