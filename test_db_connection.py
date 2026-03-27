#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para probar la conexión a la base de datos SQL Server
Ejecutar: python test_db_connection.py
"""

import logging
from server.config.database import db
from datetime import datetime

# Configurar logging para ver resultados
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def probar_conexion_simple():
    """Prueba básica de conexión"""
    print("\n" + "="*50)
    print("🔍 PROBANDO CONEXIÓN A SQL SERVER")
    print("="*50)
    
    try:
        # Obtener información de la conexión (sin exponer credenciales)
        config_info = db.config
        print(f"📡 Servidor: {config_info.server}")
        print(f"🗄️  Base de datos: {config_info.database}")
        print(f"👤 Usuario: {config_info.username}")
        print(f"⏱️  Timeout: {config_info.timeout} segundos")
        
        # Probar conexión con consulta simple
        with db.transaction() as cursor:
            # Consulta 1: Fecha y versión del servidor
            cursor.execute("""
                SELECT 
                    GETDATE() as fecha_servidor,
                    @@VERSION as version_servidor,
                    DB_NAME() as base_datos_actual
            """)
            
            row = cursor.fetchone()
            print("\n✅ CONEXIÓN EXITOSA!")
            print(f"📅 Fecha del servidor: {row[0]}")
            print(f"💾 Base de datos actual: {row[2]}")
            print(f"ℹ️  Versión: {row[1][:50]}...")  # Primeros 50 caracteres
            
        return True
        
    except Exception as e:
        print("\n❌ ERROR DE CONEXIÓN:")
        print(f"   {str(e)}")
        return False


def probar_consulta_tabla(nombre_tabla: str, limite: int = 5):
    """
    Prueba consultando una tabla específica
    
    Args:
        nombre_tabla: Nombre de la tabla a consultar
        limite: Número de registros a mostrar
    """
    print(f"\n📋 CONSULTANDO TABLA: {nombre_tabla}")
    print("-" * 40)
    
    try:
        with db.transaction() as cursor:
            # Primero verificar si la tabla existe
            cursor.execute("""
                SELECT COUNT(*) as existe
                FROM INFORMATION_SCHEMA.TABLES 
                WHERE TABLE_NAME = ?
            """, (nombre_tabla,))
            
            existe = cursor.fetchone()[0]
            
            if not existe:
                print(f"❌ La tabla '{nombre_tabla}' NO existe en la base de datos")
                
                # Mostrar tablas disponibles
                cursor.execute("""
                    SELECT TOP 10 TABLE_NAME 
                    FROM INFORMATION_SCHEMA.TABLES 
                    WHERE TABLE_TYPE = 'BASE TABLE'
                    ORDER BY TABLE_NAME
                """)
                
                tablas = cursor.fetchall()
                if tablas:
                    print("\n📌 Tablas disponibles (primeras 10):")
                    for tabla in tablas:
                        print(f"   - {tabla[0]}")
                return False
            
            # Consultar datos de la tabla
            cursor.execute(f"SELECT TOP (?) * FROM {nombre_tabla}", (limite,))
            
            # Obtener nombres de columnas
            columnas = [column[0] for column in cursor.description]
            
            # Obtener datos
            filas = cursor.fetchall()
            
            print(f"✅ Tabla encontrada: {nombre_tabla}")
            print(f"📊 Columnas: {', '.join(columnas)}")
            print(f"📏 Mostrando {len(filas)} de {limite} registros:")
            print("-" * 40)
            
            if not filas:
                print("   (No hay datos en la tabla)")
            else:
                for i, fila in enumerate(filas, 1):
                    print(f"\n   Registro {i}:")
                    for j, col in enumerate(columnas):
                        valor = fila[j]
                        # Truncar valores largos para mejor visualización
                        if isinstance(valor, str) and len(valor) > 50:
                            valor = valor[:47] + "..."
                        print(f"     {col}: {valor}")
            
            return True
            
    except Exception as e:
        print(f"❌ Error consultando tabla {nombre_tabla}: {str(e)}")
        return False


def probar_consultas_personalizadas():
    """Ejecuta consultas personalizadas para validar la conexión"""
    
    consultas = [
        {
            "nombre": "📊 Espacio en disco",
            "sql": """
                SELECT 
                    name as database_name,
                    size * 8 / 1024 as size_mb
                FROM sys.master_files
                WHERE type_desc = 'ROWS'
            """
        },
        {
            "nombre": "👥 Usuarios conectados",
            "sql": """
                SELECT COUNT(*) as conexiones_activas
                FROM sys.dm_exec_sessions
                WHERE status = 'running'
            """
        },
        {
            "nombre": "🔢 Últimas 5 tablas modificadas",
            "sql": """
                SELECT TOP 5
                    name as tabla,
                    create_date as fecha_creacion,
                    modify_date as fecha_modificacion
                FROM sys.tables
                ORDER BY modify_date DESC
            """
        }
    ]
    
    print("\n" + "="*50)
    print("🔧 EJECUTANDO CONSULTAS DE DIAGNÓSTICO")
    print("="*50)
    
    with db.transaction() as cursor:
        for consulta in consultas:
            try:
                print(f"\n{consulta['nombre']}:")
                cursor.execute(consulta['sql'])
                filas = cursor.fetchall()
                
                for fila in filas:
                    # Imprimir cada fila de manera legible
                    valores = []
                    for valor in fila:
                        if isinstance(valor, (int, float)):
                            valores.append(str(valor))
                        elif isinstance(valor, datetime):
                            valores.append(valor.strftime("%Y-%m-%d %H:%M"))
                        else:
                            valores.append(str(valor))
                    print(f"   → {' | '.join(valores)}")
                    
            except Exception as e:
                print(f"   ⚠️  Error: {str(e)}")


def menu_interactivo():
    """Menú interactivo para probar diferentes aspectos"""
    
    while True:
        print("\n" + "="*50)
        print("📌 MENÚ DE PRUEBAS DE BASE DE DATOS")
        print("="*50)
        print("1. 🔍 Probar conexión básica")
        print("2. 📋 Consultar tabla específica")
        print("3. 🔧 Ejecutar diagnósticos del servidor")
        print("4. 🚪 Salir")
        print("-" * 50)
        
        opcion = input("Selecciona una opción (1-4): ").strip()
        
        if opcion == "1":
            probar_conexion_simple()
            
        elif opcion == "2":
            tabla = input("📝 Nombre de la tabla a consultar: ").strip()
            if tabla:
                limite = input("📊 Número de registros a mostrar (Enter para 5): ").strip()
                limite = int(limite) if limite.isdigit() else 5
                probar_consulta_tabla(tabla, limite)
            else:
                print("❌ Debes ingresar un nombre de tabla")
                
        elif opcion == "3":
            probar_consultas_personalizadas()
            
        elif opcion == "4":
            print("👋 ¡Hasta luego!")
            break
            
        else:
            print("❌ Opción no válida")


if __name__ == "__main__":
    try:
        menu_interactivo()
    except KeyboardInterrupt:
        print("\n\n👋 Prueba interrumpida por el usuario")
    except Exception as e:
        print(f"\n❌ Error inesperado: {str(e)}")