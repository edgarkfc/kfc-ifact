import pyodbc

# Listar todos los drivers ODBC instalados
print("📋 Drivers ODBC instalados en tu sistema:")
print("-" * 50)

for driver in pyodbc.drivers():
    print(f"  • {driver}")

print("-" * 50)
print(f"Total: {len(pyodbc.drivers())} drivers encontrados")