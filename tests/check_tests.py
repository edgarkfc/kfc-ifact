# tests/check_tests.py
"""Verifica qué tests podrían necesitar cambios"""
import os
import re

def check_test_files():
    issues = []
    
    for root, dirs, files in os.walk('tests'):
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                with open(filepath, 'r') as f:
                    content = f.read()
                    
                    # Buscar imports que podrían romperse
                    if 'from server.controllers.helpers' in content:
                        issues.append(f"{filepath}: Importa desde controllers.helpers (aún funciona)")
                    
                    if 'from server.controllers.bills_controller' in content:
                        issues.append(f"{filepath}: Importa desde bills_controller (wrapper - funciona)")
                    
                    if 'from server.controllers.notas_credito_module' in content:
                        issues.append(f"{filepath}: Importa desde notas_credito_module (wrapper - funciona)")
    
    if issues:
        print("📋 Posibles issues encontrados:")
        for issue in issues:
            print(f"  {issue}")
    else:
        print("✅ No se encontraron imports problemáticos")

if __name__ == '__main__':
    check_test_files()