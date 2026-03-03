# C:\kfc-ifact\diagnose.py
import sys
import os

print("=" * 60)
print("DIAGNÓSTICO COMPLETO")
print("=" * 60)

print(f"\n1. Directorio actual: {os.getcwd()}")

print(f"\n2. Python path:")
for i, path in enumerate(sys.path, 1):
    print(f"   {i}. {path}")

print(f"\n3. Verificando archivos:")
files_to_check = [
    "server/app.py",
    "server/routes/api.py",
    "server/controllers/bills_controller.py",
    "server/controllers/helpers/validators.py",
    "server/controllers/helpers/cabecera_factura.py",
    "tests/conftest.py",
    "tests/test_routes.py",
]

for file in files_to_check:
    full_path = os.path.join(os.getcwd(), file)
    if os.path.exists(full_path):
        print(f"   ✓ {file}")
    else:
        print(f"   ✗ {file} (NO EXISTE)")

print(f"\n4. Verificando __init__.py:")
init_files = [
    "server/__init__.py",
    "server/routes/__init__.py",
    "server/controllers/__init__.py",
    "server/controllers/helpers/__init__.py",
    "tests/__init__.py",
]

for init_file in init_files:
    full_path = os.path.join(os.getcwd(), init_file)
    if os.path.exists(full_path):
        print(f"   ✓ {init_file}")
    else:
        print(f"   ✗ {init_file} (NO EXISTE) - DEBES CREARLO")

print(f"\n5. Recomendación:")
print("   Ejecuta estos comandos para crear los __init__.py faltantes:")
for init_file in init_files:
    full_path = os.path.join(os.getcwd(), init_file)
    if not os.path.exists(full_path):
        print(f"   echo. > {full_path}")