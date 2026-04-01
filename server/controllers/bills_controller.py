# server/controllers/bills_controller.py
from server.controllers.helpers.create_invoice import cabeceraFacturas, factura_productos, factura_pagos
from server.controllers.helpers.print_messages import print_message
from server.controllers.helpers.polices import validar_mensaje_qr
from server.controllers.helpers.validators import (FacturaSchema)
from marshmallow import ValidationError
import logging
from datetime import datetime

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def validar_factura(datos):
    """
    Función SOLO para validar la factura
    Retorna los datos validados si son correctos, o lanza ValidationError
    """
    try:
        schema = FacturaSchema()
        datos_validados = schema.load(datos)
        logger.info("✅ Factura validada correctamente")
        return datos_validados
    except ValidationError as e:
        logger.error(f"❌ Error de validación: {e.messages}")
        raise
    except Exception as e:
        logger.error(f"❌ Error inesperado en validación: {str(e)}")
        raise ValidationError({"error": str(e)})

def procesar_factura(datos_validados):
    """
    Función para procesar una factura YA VALIDADA
    """
    try:
        logger.info("🚀 Procesando factura...")
        
        # Obtener configuración de impresora
        config_impresora = datos_validados.get('config_impresora', {})
        
        # Armar cabecera y cliente
        cabecera_cliente = cabeceraFacturas(datos_validados)
        
        # Armar líneas de factura y productos
        factura_lines = []
        detail_productos = factura_productos(datos_validados, factura_lines)
        
        # Armar pagos
        pagos_factura = factura_pagos(factura_lines, datos_validados)
        
        # Unificar factura
        factura_unificada = cabecera_cliente + detail_productos['factura']
        
        # Verificar si se debe imprimir mensaje QR
        impresion_msgqr = validar_mensaje_qr(config_impresora.get('impresion_msgqr', False))
        
        if impresion_msgqr:
            logger.info("🖨️ Imprimiendo mensaje QR...")
            resultado_impresion = print_message(factura_unificada)
            factura_unificada = resultado_impresion['factura']
        
        # Agregar línea final
        factura_unificada.append("199\n")
        
        resultado = {
            "cabecera_cliente": cabecera_cliente,
            "detail_productos": detail_productos,
            "pagos_factura": pagos_factura,
            "factura_unificada": factura_unificada,
            "metadata": {
                "total_items": len(detail_productos.get('factura', [])),
                "total_pagos": len(pagos_factura),
                "factura_completa": len(factura_unificada)
            }
        }
        
        logger.info("✅ Factura procesada exitosamente")
        return resultado
        
    except Exception as e:
        logger.error(f"❌ Error al procesar factura: {str(e)}")
        import traceback
        traceback.print_exc()
        raise

def armar_factura(datos):
    """
    Función original para compatibilidad
    Combina validación y procesamiento
    """
    try:
        datos_validados = validar_factura(datos)
        return procesar_factura(datos_validados)
    except ValidationError as e:
        logger.error(f"Error de validación: {e.messages}")
        return {"error": "validacion_fallida", "detalles": e.messages}
    except Exception as e:
        logger.error(f"Error en armar_factura: {e}")
        import traceback
        traceback.print_exc()
        return {"error": "procesamiento_fallido", "detalle": str(e)}

# ============================================
# NUEVAS FUNCIONES PARA CONTROLADOR CON RESPUESTAS FORMATEADAS
# ============================================

def validar_factura_controller(datos):
    """
    Controlador para validación de factura
    Retorna tupla (datos, error, status_code)
    """
    try:
        # Validar factura
        datos_validados = validar_factura(datos)
        
        # Preparar respuesta exitosa
        respuesta = {
            'success': True,
            'message': 'Factura válida',
            'timestamp': datetime.now().isoformat(),
            'data': {
                'validacion': 'exitosa',
                'resumen': {
                    'cliente': datos_validados.get('cliente', {}).get('cliente_nombres'),
                    'total_factura': datos_validados.get('cabecera_factura', {}).get('cabfact_total'),
                    'items': len(datos_validados.get('detalle_factura', [])),
                    'formas_pago': len(datos_validados.get('formas_pago', []))
                }
            }
        }
        return respuesta, None, 200
        
    except ValidationError as e:
        respuesta = {
            'success': False,
            'message': 'Error de validación en la factura',
            'errors': e.messages,
            'timestamp': datetime.now().isoformat()
        }
        return respuesta, e, 422
        
    except Exception as e:
        logger.error(f"Error inesperado en validar_factura_controller: {str(e)}", exc_info=True)
        respuesta = {
            'success': False,
            'message': 'Error interno del servidor',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }
        return respuesta, e, 500

def procesar_factura_controller(datos):
    """
    Controlador para procesamiento de factura
    Retorna tupla (datos, error, status_code)
    """
    try:
        # Validar factura
        datos_validados = validar_factura(datos)
        
        # Procesar factura
        factura_procesada = procesar_factura(datos_validados)
        
        # Preparar respuesta exitosa
        respuesta = {
            'success': True,
            'message': 'Factura procesada exitosamente',
            'timestamp': datetime.now().isoformat(),
            'data': factura_procesada
        }
        return respuesta, None, 200
        
    except ValidationError as e:
        respuesta = {
            'success': False,
            'message': 'Error de validación',
            'errors': e.messages,
            'timestamp': datetime.now().isoformat()
        }
        return respuesta, e, 422
        
    except Exception as e:
        logger.error(f"Error inesperado en procesar_factura_controller: {str(e)}", exc_info=True)
        respuesta = {
            'success': False,
            'message': 'Error interno del servidor',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }
        return respuesta, e, 500

def armar_factura_controller(datos):
    """
    Controlador que combina validación y procesamiento
    Retorna tupla (datos, error, status_code)
    """
    try:
        # Armar factura (validación + procesamiento)
        resultado = armar_factura(datos)
        
        # Verificar si hubo error en el procesamiento
        if isinstance(resultado, dict) and 'error' in resultado:
            respuesta = {
                'success': False,
                'message': resultado.get('error', 'Error al procesar factura'),
                'details': resultado.get('detalles', resultado.get('detalle', '')),
                'timestamp': datetime.now().isoformat()
            }
            return respuesta, Exception(resultado.get('error')), 422
        
        # Respuesta exitosa
        respuesta = {
            'success': True,
            'message': 'Factura armada exitosamente',
            'timestamp': datetime.now().isoformat(),
            'data': resultado
        }
        return respuesta, None, 200
        
    except Exception as e:
        logger.error(f"Error inesperado en armar_factura_controller: {str(e)}", exc_info=True)
        respuesta = {
            'success': False,
            'message': 'Error interno del servidor',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }
        return respuesta, e, 500

def health_check_controller():
    """
    Controlador para health check
    """
    return {
        'success': True,
        'message': 'Servicio de facturas operativo',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    }, 200