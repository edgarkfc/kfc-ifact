# C:\kfc-ifact\check_init.py
import os

print("Verificando archivos __init__.py:\n")

paths = [
    "server/__init__.py",
    "server/routes/__init__.py", 
    "server/controllers/__init__.py",
    "server/controllers/helpers/__init__.py",
    "tests/__init__.py"
]

for path in paths:
    full_path = os.path.join(os.getcwd(), path)
    if os.path.exists(full_path):
        print(f"✅ {path} - CORRECTO")
        # Mostrar los primeros caracteres para verificar que no está vacío
        with open(full_path, 'r') as f:
            content = f.read()
            if content:
                print(f"   Contenido: {content[:50]}...")
            else:
                print(f"   (archivo vacío - OK)")
    else:
        incorrect = path.replace("__init__.py", "init.py")
        if os.path.exists(os.path.join(os.getcwd(), incorrect)):
            print(f"❌ {path} - INCORRECTO (tienes {incorrect})")
        else:
            print(f"❌ {path} - FALTA")