🧾 KFC-IFACT - Sistema de Facturación Electrónica
📋 Descripción General
API REST para gestión de facturas electrónicas y notas de crédito, construida con Flask y SQL Server. El sistema genera códigos QR personalizados y mensajes de pie de página configurables desde base de datos, permitiendo una experiencia de impresión flexible y dinámica para impresoras fiscales.

🛠️ Tecnologías Utilizadas
Tecnología	Versión	Propósito
Python	3.14	Lenguaje principal
Flask	3.1.3	Framework web
pyodbc	5.3.0	Conector a SQL Server
Marshmallow	4.3.0	Validación y serialización de datos
Alembic	1.18.4	Migraciones de base de datos
DearPyGui	2.2	Interfaz gráfica cliente
Pytest	9.0.2	Pruebas unitarias
python-dotenv	1.2.2	Variables de entorno
🏗️ Arquitectura del Proyecto
text
kfc-ifact/
├── .env                              # Variables de entorno
├── requirements.txt                  # Dependencias del proyecto
│
├── server/
│   ├── app.py                        # Entry point (Flask factory)
│   │
│   ├── config/
│   │   └── database.py               # Conexión a BD (Singleton + Context Manager)
│   │
│   ├── routes/
│   │   └── api.py                    # Endpoints (Blueprints)
│   │
│   ├── controllers/
│   │   ├── base_controller.py        # Clase abstracta (Template Method)
│   │   ├── bills_controller.py       # Wrapper facturas (Adapter)
│   │   ├── factura_controller.py     # Controller facturas
│   │   ├── nota_credito_controller.py # Controller notas crédito
│   │   ├── notas_credito_module.py   # Wrapper notas crédito
│   │   └── helpers/
│   │       ├── algortimoqr.py        # Algoritmo personalizado QR
│   │       ├── create_invoice.py     # Formato para impresora fiscal
│   │       └── print_messages.py     # Helper mensajes impresión
│   │
│   ├── services/
│   │   ├── factura_service.py        # Lógica negocio facturas (QR + mensajes)
│   │   ├── nota_credito_service.py   # Lógica negocio notas crédito
│   │   ├── impresion_service.py      # Formateo para impresión térmica
│   │   ├── qr_service.py             # Generación de códigos QR
│   │   └── print_message_service.py  # Servicio mensajes desde BD
│   │
│   ├── schemas/
│   │   ├── factura_schema.py         # Validación facturas (Marshmallow)
│   │   ├── nota_credito_schema.py    # Validación notas crédito
│   │   └── componentes.py            # Schemas reutilizables
│   │
│   └── repositories/
│       ├── pivotqrs_repository.py    # Parámetros para QR
│       └── print_messages_repository.py # Mensajes desde BD
│
├── client/
│   └── views/                        # Interfaz DearPyGui
│
├── tests/
│   ├── fixtures/                     # Datos de prueba
│   └── test_*.py                     # Pruebas unitarias
│
└── venv/                             # Entorno virtual
🎨 Patrones de Diseño Implementados
Patrón	Ubicación	Beneficio
Template Method	base_controller.py	Define esqueleto del algoritmo, subclases implementan detalles
Adapter/Wrapper	bills_controller.py	Compatibilidad retrocompatible sin romper código existente
Factory Method	app.py: create_app()	Creación centralizada y configurable de la app
Singleton	config/database.py	Una sola instancia de configuración de BD
Blueprint	routes/api.py	Modularización de rutas por dominio
Service Layer	services/*.py	Encapsula lógica de negocio compleja
Repository	repositories/*.py	Abstracción del acceso a datos
DTO/Schema	schemas/*.py	Validación y transformación de datos
🔄 Flujo de Procesamiento
Diagrama de Secuencia - Factura con QR y Mensajes
text
Cliente (DearPyGui)          API Route              Controller           Service              Repository            BD
      │                          │                      │                    │                     │                │
      │ POST /api/facturas/procesar                    │                    │                     │                │
      │─────────────────────────▶│                      │                    │                     │                │
      │                          │                      │                    │                     │                │
      │                          │ handle_request()     │                    │                     │                │
      │                          │─────────────────────▶│                    │                     │                │
      │                          │                      │                    │                     │                │
      │                          │                      │ validar_documento()│                     │                │
      │                          │                      │───────────────────▶│ Schema              │                │
      │                          │                      │                    │                     │                │
      │                          │                      │ datos_validados    │                     │                │
      │                          │                      │◀───────────────────│                     │                │
      │                          │                      │                    │                     │                │
      │                          │                      │ procesar_documento()│                    │                │
      │                          │                      │───────────────────▶│ FacturaService      │                │
      │                          │                      │                    │                     │                │
      │                          │                      │                    │ procesar_qr()       │                │
      │                          │                      │                    │────────────────────▶│ QRService       │
      │                          │                      │                    │                     │                │
      │                          │                      │                    │ get_parametros_qr()│                │
      │                          │                      │                    │─────────────────────────────────────▶│
      │                          │                      │                    │                     │                │
      │                          │                      │                    │ qr_texto: yXXXXX   │                │
      │                          │                      │                    │◀─────────────────────────────────────│
      │                          │                      │                    │                     │                │
      │                          │                      │                    │ get_messages()      │                │
      │                          │                      │                    │─────────────────────────────────────▶│
      │                          │                      │                    │                     │                │
      │                          │                      │                    │ mensajes (i01, i02) │                │
      │                          │                      │                    │◀─────────────────────────────────────│
      │                          │                      │                    │                     │                │
      │                          │                      │ resultado          │                     │                │
      │                          │                      │◀───────────────────│                     │                │
      │                          │                      │                    │                     │                │
      │                          │ respuesta (200)      │                    │                     │                │
      │                          │◀─────────────────────│                    │                     │                │
      │                          │                      │                    │                     │                │
      │ JSON Response            │                      │                    │                     │                │
      │◀─────────────────────────│                      │                    │                     │                │
📡 Endpoints de la API
Facturas
Método	Endpoint	Body	Respuesta exitosa	Códigos
POST	/api/facturas/procesar	Factura JSON	{success, message, data}	200, 422, 500
Notas de Crédito
Método	Endpoint	Body	Respuesta exitosa	Códigos
POST	/api/notas-credito/procesar	NotaCredito JSON	{success, message, data}	200, 422, 500
📦 Estructura de Datos (Schemas)
{
  "factura": {
    "restaurante": {
      "restaurante": "K098",
      "rest_id": 45,
      "impuesto_rest": true,
      "nro_estacion": 1
    },
    "config_impresora": {
      "impresion_qr": true,
      "impresion_msgqr": true,
      "impresion_cupon": false
    },
    "cabecera_factura": {
      "cabfact_id": "K098F000000576",
      "cabfact_nrofact_nc": "0000",
      "delivery_id": "PEYA-1921213682",
      "cabfact_fechacreacion": "2026-02-26T16:29:57.133",
      "cabfact_subtotal": 4183.1724,
      "cabfact_iva": 669.31,
      "cabfact_total": 4852.48,
      "cabfact_valor_descuento": 0,
      "cabfact_porcentaje_descuento": 0,
      "cabfact_cajero": "lgarcia",
      "cabfact_tasa_conversion": 414.04
    },
    "detalle_factura": [
      {
        "detallefactura_id": "8DBF8DE7-5113-F111-ADF8-D0C1B5009507",
        "dtfacplu_id": 4178,
        "dtfac_cantidad": 2,
        "dtfac_precio_unitario": 2426.24,
        "dtfac_iva": 334.65,
        "dtfac_total": 4852.48,
        "aplicaImpuesto1": 1,
        "aplicaImpuesto2": 0,
        "aplicaImpuesto3": 0,
        "aplicaImpuesto4": 0,
        "aplicaImpuesto5": 0,
        "dtfac_valor_descuento": 0,
        "dtfac_porcentaje_descuento": 0,
        "dtfac_totaldesc":0,
        "dtfac_ivadesc": 0,
        "dtfac_descripcion": "COMBO 2PZ CON PAPAS"
      },
      {
        "detallefactura_id": "8CBF8DE7-5113-F111-ADF8-D0C1B5009507",        
        "dtfacplu_id": 258,
        "dtfac_cantidad": 1,
        "dtfac_precio_unitario": 0,
        "dtfac_iva": 0,
        "dtfac_total": 0,
        "aplicaImpuesto1": 1,
        "aplicaImpuesto2": 0,
        "aplicaImpuesto3": 0,
        "aplicaImpuesto4": 0,
        "aplicaImpuesto5": 0,
        "dtfac_valor_descuento": 0,
        "dtfac_porcentaje_descuento": 0,
        "dtfac_totaldesc": 0,
        "dtfac_ivadesc": 0,
        "dtfac_descripcion": ".No"        
      },
      {
        "detallefactura_id": "8BBF8DE7-5113-F111-ADF8-D0C1B5009507",       
        "dtfacplu_id": 246,
        "dtfac_cantidad": 1,
        "dtfac_precio_unitario": 0,
        "dtfac_iva": 0,
        "dtfac_total": 0,
        "aplicaImpuesto1": 1,
        "aplicaImpuesto2": 0,
        "aplicaImpuesto3": 0,
        "aplicaImpuesto4": 0,
        "aplicaImpuesto5": 0,
        "dtfac_valor_descuento": 0,
        "dtfac_porcentaje_descuento": 0,
        "dtfac_totaldesc": 0,
        "dtfac_ivadesc": 0,
        "dtfac_descripcion": "..KOLITA"        
      }
    ],
    "cliente": {
      "cliente_id": "C62EB822-216B-497A-8F61-AA1F2DD3945C",
      "cliente_documento": "V20289719",
      "cliente_nombres": "ALEJANDRO",
      "cliente_apellidos": null,
      "cliente_telefono": "04241572784",
      "cliente_direccion": "NULL",
      "cliente_email": "AAA@INBOX.COM"
    },
    "formas_pago": [
      {
        "formapagoactura_id": "8FBF8DE7-5113-F111-ADF8-D0C1B5009507",
        "formapago_id": "5917064E-A357-EC11-94F6-0050F2D50918",
        "fpf_total_pagar": 4552.48,
        "formapago": "16"
      },
      {
        "formapagoactura_id": "8FBF8DE7-5113-F111-ADF8-D0C1B5009507",
        "formapago_id": "5917064E-A357-EC11-94F6-0050F2D50918",
        "fpf_total_pagar": 300.00,
        "formapago": "01"
      }
    ]
  }
}
Configuración de Impresora (config_impresora)
Campo	Tipo	Descripción
impresion_qr	boolean	Activa generación de código QR
impresion_msgqr	boolean	Activa mensajes personalizados desde BD
impresion_cupon	boolean	Reservado para cupones de descuento
💾 Base de Datos
Tabla pivotqrs - Parámetros para QR
Campo	Tipo	Descripción
id	int	Identificador único
nropases	int	Número de pases para el algoritmo
nrotarjetas	int	Contador de tarjetas (se incrementa automáticamente)
hora	int	Horas de expiración
minutos	int	Minutos de expiración
status	bit	1=ACTIVO, 0=INACTIVO
Datos de ejemplo:

sql
INSERT INTO pivotqrs (nropases, nrotarjetas, hora, minutos, status)
VALUES (4, 300, 1, 0, 1);
Tabla print_messages - Mensajes de Impresión
Campo	Tipo	Descripción
id	int	Identificador único
code	varchar(20)	Código del mensaje (i01, i02, etc.)
content	varchar(500)	Contenido del mensaje
order	int	Orden de visualización
is_active	bit	1=activo, 0=inactivo
Datos de ejemplo:

sql
INSERT INTO print_messages (code, content, [order], is_active) VALUES 
('i01', '                         _ _ _ _ _', 1, 1),
('i02', 'USE EL QR IMPRESO PARA          |', 2, 1),
('i03', 'INGRESAR AL SANITARIO_ _ _ _    |', 3, 1);
📊 Códigos QR - Formato
El sistema genera códigos QR con el siguiente formato:

text
y{trama_numerica}
Ejemplo: y2330043238

Parte	Descripción
y	Prefijo fijo (siempre presente)
2330043238	Trama numérica generada por algoritmo personalizado
Algoritmo QR
Lee parámetros desde la tabla pivotqrs

Calcula la trama basada en fecha, hora, pases y tarjetas

Incrementa automáticamente el contador de tarjetas

Retorna el número generado con prefijo y

🚀 Instalación y Configuración
1. Clonar repositorio
bash
git clone <repository-url>
cd kfc-ifact
2. Crear entorno virtual
bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
3. Instalar dependencias
bash
pip install -r requirements.txt
4. Configurar variables de entorno (.env)
env
# Base de Datos
DB_DRIVER=ODBC Driver 17 for SQL Server
DB_SERVER=localhost
DB_PORT=1433
DB_NAME=facturacion_db
DB_USER=sa
DB_PASSWORD=TuContraseña123
DB_TIMEOUT=30
DB_ENCRYPT=yes
DB_TRUST_SERVER_CERTIFICATE=yes

# Flask
FLASK_DEBUG=True
FLASK_HOST=0.0.0.0
FLASK_PORT=5000
5. Crear tablas en la base de datos
sql
-- Tabla para parámetros QR
CREATE TABLE pivotqrs (
    id INT IDENTITY(1,1) PRIMARY KEY,
    nropases INT NOT NULL DEFAULT 0,
    nrotarjetas INT NOT NULL DEFAULT 0,
    hora INT NOT NULL DEFAULT 0,
    minutos INT NOT NULL DEFAULT 0,
    status BIT NOT NULL DEFAULT 1,
    created_at DATETIME DEFAULT GETDATE(),
    updated_at DATETIME DEFAULT GETDATE()
);

-- Tabla para mensajes de impresión
CREATE TABLE print_messages (
    id INT IDENTITY(1,1) PRIMARY KEY,
    code VARCHAR(20) NOT NULL,
    content VARCHAR(500) NOT NULL,
    [order] INT NOT NULL DEFAULT 0,
    is_active BIT NOT NULL DEFAULT 1,
    created_at DATETIME DEFAULT GETDATE(),
    updated_at DATETIME DEFAULT GETDATE()
);

-- Insertar datos de ejemplo
INSERT INTO pivotqrs (nropases, nrotarjetas, hora, minutos, status) VALUES (4, 300, 1, 0, 1);

INSERT INTO print_messages (code, content, [order], is_active) VALUES 
('i01', '                         _ _ _ _ _', 1, 1),
('i02', 'USE EL QR IMPRESO PARA          |', 2, 1),
('i03', 'INGRESAR AL SANITARIO_ _ _ _    |', 3, 1);
6. Verificar conexión a base de datos
bash
python -c "from server.config.database import db; print(db.execute_query('SELECT GETDATE()', fetch=True))"
7. Ejecutar la aplicación
bash
python server/app.py
🧪 Ejemplos de Uso
Procesar Factura con QR y Mensajes
Respuesta Exitosa
{
    "data": {
        "cabecera_cliente": [
            "iS* ALEJANDRO\n",
            "iR* V20289719\n",
            "i03Direccion: NULL\n",
            "i04Telefono: 04241572784\n",
            "i05Transaccion: K098F000000576\n",
            "i06Orden Delivery: PEYA-1921213682\n"
        ],
        "detail_productos": {
            "factura": [
                "!0000024262400000002COMBO 2PZ CON PAPAS\n",
                "@.No\n",
                "@..KOLITA\n"
            ],
            "subtotales": {
                "total_bruto": 0.0,
                "total_descuentos": 0.0,
                "total_iva": 0.0,
                "total_neto": 4852.48
            }
        },
        "factura_unificada": [
            "iS* ALEJANDRO\n",
            "iR* V20289719\n",
            "i03Direccion: NULL\n",
            "i04Telefono: 04241572784\n",
            "i05Transaccion: K098F000000576\n",
            "i06Orden Delivery: PEYA-1921213682\n",
            "!0000024262400000002COMBO 2PZ CON PAPAS\n",
            "@.No\n",
            "@..KOLITA\n",
            "3\n",
            "y1244210199\n",
            "i01                         _ _ _ _ _  \n",
            "i02 USE EL QR IMPRESO PARA          | \n",
            "i03 INGRESAR AL SANITARIO_ _ _ _    | \n",
            "i04                              |   | \n",
            "i05                              |   | \n",
            "i06                              |   | \n",
            "i07                             \\|   |/  \n",
            "i08                              \\   / \n",
            "i09                               \\ / \n",
            "216000000455248\n",
            "201000000030000\n",
            "199\n"
        ],
        "metadata": {
            "factura_completa": 23,
            "iva": 669.31,
            "subtotal": 4183.1724,
            "total_factura": 4852.48,
            "total_items": 3,
            "total_pagos": 2
        },
        "pagos_factura": [
            {
                "forma": "16",
                "linea": "216000000455248\n",
                "valor": 4552.48
            },
            {
                "forma": "01",
                "linea": "201000000030000\n",
                "valor": 300.0
            }
        ],
        "tipo_documento": "FACTURA"
    },
    "message": "FACTURA procesada exitosamente",
    "success": true,
    "timestamp": "2026-04-10T15:23:55.079826"
}
Procesar Nota de Crédito (sin QR)

{
  "nota_credito": {
    "restaurante": {
      "restaurante": "K098",
      "rest_id": 45,
      "impuesto_rest": true,
      "nro_estacion": 1
    },
    "config_impresora": {
      "impresion_qr": true,
      "impresion_msgqr": true,
      "impresion_cupon": false
    },
    "cabecera_factura": {
      "cabfact_id": "K098F000000576",
      "cabfact_nrofact_nc": "0000",
      "delivery_id": "PEYA-1921213682",
      "cabfact_fechacreacion": "2026-02-26T16:29:57.133",
      "cabfact_subtotal": 4183.1724,
      "cabfact_iva": 669.31,
      "cabfact_total": 4852.48,
      "cabfact_valor_descuento": 0,
      "cabfact_porcentaje_descuento": 0,
      "cabfact_cajero": "lgarcia",
      "cabfact_tasa_conversion": 414.04
    },
    "detalle_factura": [
      {
        "detallefactura_id": "8DBF8DE7-5113-F111-ADF8-D0C1B5009507",
        "dtfacplu_id": 4178,
        "dtfac_cantidad": 2,
        "dtfac_precio_unitario": 2426.24,
        "dtfac_iva": 334.65,
        "dtfac_total": 4852.48,
        "aplicaImpuesto1": 1,
        "aplicaImpuesto2": 0,
        "aplicaImpuesto3": 0,
        "aplicaImpuesto4": 0,
        "aplicaImpuesto5": 0,
        "dtfac_valor_descuento": 0,
        "dtfac_porcentaje_descuento": 0,
        "dtfac_totaldesc":0,
        "dtfac_ivadesc": 0,
        "dtfac_descripcion": "COMBO 2PZ CON PAPAS"
      },
      {
        "detallefactura_id": "8CBF8DE7-5113-F111-ADF8-D0C1B5009507",        
        "dtfacplu_id": 258,
        "dtfac_cantidad": 1,
        "dtfac_precio_unitario": 0,
        "dtfac_iva": 0,
        "dtfac_total": 0,
        "aplicaImpuesto1": 1,
        "aplicaImpuesto2": 0,
        "aplicaImpuesto3": 0,
        "aplicaImpuesto4": 0,
        "aplicaImpuesto5": 0,
        "dtfac_valor_descuento": 0,
        "dtfac_porcentaje_descuento": 0,
        "dtfac_totaldesc": 0,
        "dtfac_ivadesc": 0,
        "dtfac_descripcion": ".No"        
      },
      {
        "detallefactura_id": "8BBF8DE7-5113-F111-ADF8-D0C1B5009507",       
        "dtfacplu_id": 246,
        "dtfac_cantidad": 1,
        "dtfac_precio_unitario": 0,
        "dtfac_iva": 0,
        "dtfac_total": 0,
        "aplicaImpuesto1": 1,
        "aplicaImpuesto2": 0,
        "aplicaImpuesto3": 0,
        "aplicaImpuesto4": 0,
        "aplicaImpuesto5": 0,
        "dtfac_valor_descuento": 0,
        "dtfac_porcentaje_descuento": 0,
        "dtfac_totaldesc": 0,
        "dtfac_ivadesc": 0,
        "dtfac_descripcion": "..KOLITA"        
      }
    ],
    "cliente": {
      "cliente_id": "C62EB822-216B-497A-8F61-AA1F2DD3945C",
      "cliente_documento": "V20289719",
      "cliente_nombres": "ALEJANDRO",
      "cliente_apellidos": null,
      "cliente_telefono": "04241572784",
      "cliente_direccion": "NULL",
      "cliente_email": "AAA@INBOX.COM"
    },
    "formas_pago": [
      {
        "formapagoactura_id": "8FBF8DE7-5113-F111-ADF8-D0C1B5009507",
        "formapago_id": "5917064E-A357-EC11-94F6-0050F2D50918",
        "fpf_total_pagar": 4552.48,
        "formapago": "16"
      },
      {
        "formapagoactura_id": "8FBF8DE7-5113-F111-ADF8-D0C1B5009507",
        "formapago_id": "5917064E-A357-EC11-94F6-0050F2D50918",
        "fpf_total_pagar": 300.00,
        "formapago": "01"
      }
    ]
  }
}

🧪 Pruebas
Ejecutar todas las pruebas
bash
pytest tests/
Ejecutar con cobertura
bash
pytest --cov=server tests/
Probar QR directamente
bash
python -c "from server.services.qr_service import QRService; qr = QRService(); print(qr.generar_trama_completa())"
Probar mensajes desde BD
bash
python -c "from server.repositories.print_messages_repository import PrintMessagesRepository; repo = PrintMessagesRepository(); print(repo.get_all_active_ordered())"
📋 Próximos Pasos (TODO)
Completados ✅
Configuración inicial del proyecto

Conexión a base de datos (SQL Server + pyodbc)

Estructura de controladores con Template Method

Schemas de validación con Marshmallow

Servicio de facturas con QR

Servicio de notas de crédito

Algoritmo personalizado para QR

Mensajes personalizados desde base de datos

Integración de QR y mensajes en facturas

Formato de salida para impresora fiscal

Pendientes ⏳
Implementar impresion_cupon (cupones de descuento)

Agregar autenticación JWT

Documentar API con Swagger/OpenAPI

Implementar caché de consultas frecuentes (Redis)

Agregar rate limiting

Implementar logging estructurado (JSON)

Crear script de despliegue con Docker

Agregar CI/CD con GitHub Actions

👥 Contribuidores
[Tu nombre / equipo de desarrollo]

📄 Licencia
[Especificar licencia - MIT, Apache, etc.]

🙏 Agradecimientos
Flask por el framework web

Marshmallow por la validación elegante

pyodbc por la conexión a SQL Server

DearPyGui por la interfaz gráfica

Documentación generada a partir del código fuente
Última actualización: 2024
Versión de la API: 2.0.0