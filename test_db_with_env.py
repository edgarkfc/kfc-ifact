#!/usr/bin/env python
# test_db_with_env.py - Prueba la conexión usando variables de entorno

from server.config.database import db
import logging

logging.basicConfig(level=logging.INFO)


def test_conexion():
    """Prueba la conexión exactamente como tu script exitoso"""
    
    print("\n" + "="*60)
    print("🔍 PROBANDO CONEXIÓN A SQL SERVER DESDE CONFIGURACIÓN .ENV")
    print("="*60)
    
    # Mostrar configuración (sin password)
    print(f"\n📋 Configuración:")
    print(f"   Driver: {db.config.driver}")
    print(f"   Servidor: {db.config.server}")
    print(f"   Base de datos: {db.config.database}")
    print(f"   Usuario: {db.config.username}")
    
    try:
        with db.transaction() as cursor:
            # Misma consulta que funcionó en tu script
            cursor.execute("SELECT name FROM sys.databases")
            
            print("\n📚 Bases de datos disponibles:")
            for row in cursor.fetchall():
                print(f"   - {row[0]}")
            
            # También probar con la base de datos actual
            cursor.execute("SELECT DB_NAME() as current_db")
            current_db = cursor.fetchone()[0]
            print(f"\n🎯 Base de datos actual: {current_db}")
            
            print("\n✅ CONEXIÓN EXITOSA!")
            return True
            
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        return False


def test_consulta_facturas():
    """Prueba consultando tablas de facturas"""
    
    print("\n" + "="*60)
    print("🔍 BUSCANDO TABLAS DE FACTURAS")
    print("="*60)
    
    try:
        with db.transaction() as cursor:
            # Buscar tablas relacionadas con facturas
            cursor.execute("""
                SELECT 
                    TABLE_SCHEMA,
                    TABLE_NAME,
                    TABLE_TYPE
                FROM INFORMATION_SCHEMA.TABLES 
                WHERE TABLE_NAME LIKE '%factura%' 
                   OR TABLE_NAME LIKE '%Factura%'
                   OR TABLE_NAME LIKE '%FACTURA%'
                ORDER BY TABLE_NAME
            """)
            
            tablas = cursor.fetchall()
            
            if tablas:
                print(f"\n📋 Tablas relacionadas con facturas ({len(tablas)}):")
                for tabla in tablas:
                    print(f"   - {tabla[0]}.{tabla[1]} ({tabla[2]})")
                    
                    # Contar registros
                    cursor.execute(f"SELECT COUNT(*) FROM {tabla[0]}.{tabla[1]}")
                    count = cursor.fetchone()[0]
                    print(f"     Registros: {count}")
            else:
                print("\n❌ No se encontraron tablas relacionadas con facturas")
                
    except Exception as e:
        print(f"❌ Error en consulta: {e}")


if __name__ == "__main__":
    # Ejecutar pruebas
    if test_conexion():
        test_consulta_facturas()
    
    # Cerrar conexión
    db.close()