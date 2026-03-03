# C:\kfc-ifact\check_structure.py
import os

def list_files(startpath):
    for root, dirs, files in os.walk(startpath):
        level = root.replace(startpath, '').count(os.sep)
        indent = ' ' * 4 * level
        print(f'{indent}{os.path.basename(root)}/')
        subindent = ' ' * 4 * (level + 1)
        for f in files:
            if f.endswith('.py'):
                print(f'{subindent}{f}')

print("Estructura actual del proyecto:")
list_files('.')