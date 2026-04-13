#!/usr/bin/env python
# test_db_connection.py - Prueba completa de conexión a BD

import sys
import logging
from pathlib import Path

# Configurar logging para ver todo
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Agregar la ruta del proyecto si es necesario
sys.path.insert(0, str(Path(__file__).parent))

try:
    # Importar tu módulo de base de datos
    from server.config.database import DatabaseConnection, DatabaseConfig
    
    print("\n" + "="*60)
    print("🔍 INICIANDO PRUEBAS DE BASE DE DATOS")
    print("="*60)
    
    # 1. Verificar configuración cargada
    print("\n📋 1. Verificando configuración...")
    config = DatabaseConfig()
    print(f"   ✅ Configuración cargada: {config}")
    print(f"   📍 Servidor: {config.server}")
    print(f"   💾 Base de datos: {config.database}")
    print(f"   👤 Usuario: {config.username}")
    
    # 2. Probar conexión
    print("\n🔌 2. Probando conexión a la base de datos...")
    db = DatabaseConnection()
    
    try:
        conn = db.connect()
        print("   ✅ Conexión establecida exitosamente!")
        
        # 3. Probar consulta simple
        print("\n📊 3. Probando consulta SELECT 1...")
        cursor = conn.cursor()
        cursor.execute("SELECT 1 AS test, GETDATE() AS fecha_actual")
        resultado = cursor.fetchone()
        print(f"   ✅ Consulta exitosa: {resultado}")
        
        # 4. Probar consulta a una tabla real (opcional)
        print("\n🗂️ 4. Probando consulta a tablas del sistema...")
        cursor.execute("""
            SELECT TOP 5 
                TABLE_SCHEMA, 
                TABLE_NAME 
            FROM INFORMATION_SCHEMA.TABLES 
            WHERE TABLE_TYPE = 'BASE TABLE'
            ORDER BY TABLE_NAME
        """)
        tablas = cursor.fetchall()
        print(f"   ✅ Se encontraron {len(tablas)} tablas en la base de datos:")
        for tabla in tablas[:5]:
            print(f"      - {tabla[0]}.{tabla[1]}")
        
        # 5. Probar método execute_query
        print("\n🔄 5. Probando método execute_query...")
        resultados = db.execute_query(
            "SELECT TOP 3 * FROM INFORMATION_SCHEMA.TABLES", 
            fetch=True
        )
        if resultados:
            print(f"   ✅ execute_query funcionó, obtuvo {len(resultados)} registros")
        
        print("\n" + "="*60)
        print("🎉 ¡TODAS LAS PRUEBAS PASARON EXITOSAMENTE!")
        print("   La conexión a la base de datos funciona correctamente")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ ERROR durante las pruebas: {str(e)}")
        print("\n🔧 Posibles soluciones:")
        print("   1. Verifica que el archivo .env tenga las credenciales correctas")
        print("   2. Verifica que el driver ODBC esté instalado")
        print("   3. Verifica que el servidor de BD esté accesible")
        sys.exit(1)
        
    finally:
        db.close()
        print("\n🔒 Conexión cerrada")
        
except ImportError as e:
    print(f"\n❌ Error de importación: {e}")
    print("\n🔧 Verifica que las librerías estén instaladas:")
    print("   pip install pyodbc python-dotenv")
    sys.exit(1)