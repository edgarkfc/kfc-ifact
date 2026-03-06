# routes/api.py
from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from server.controllers.bills_controller import armar_factura 
import logging
from datetime import datetime

# Configurar logger
logger = logging.getLogger(__name__)

# Crear el Blueprint para facturas
# Un Blueprint es como un submódulo de rutas que puedes registrar en la app principal
facturas_bp = Blueprint('facturas', __name__, url_prefix='/api/facturas')

# ============================================
# RUTAS PRINCIPALES
# ============================================

@facturas_bp.route('/validar', methods=['POST'])
def validar_factura():
    """
    Endpoint para validar una factura completa
    ---
    Espera un JSON con estructura de factura
    """
    try:
       
        # 1. Verificar que el contenido sea JSON
        if not request.is_json:
            return jsonify({'success': False, 'message': 'No viene JSON en la solicitud'}), 400
        
        # 2. Obtener datos del request
        datos = request.get_json()
        #logger.debug(f"JSON recibido: {datos}")
        cliente= armar_factura(datos)
        # 3. Validar usando la función principal
          # Esto validará la estructura general y tipos básicos
        
          # Aquí puedes hacer validaciones más complejas o cálculos adicionales
        # 4. Responder según resultado
       
        
        # 5. Éxito - datos válidos
        return jsonify({
            'success': True,
            'message': 'Factura válida',
            'timestamp': datetime.now().isoformat(),
            'data': cliente
        }), 200
        
    except ValidationError as e:
        # Error de validación de Marshmallow
        logger.error(f"ValidationError: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Error de validación',
            'errors': e.messages
        }), 422
        
    except Exception as e:
        # Error interno del servidor
        logger.error(f"Error inesperado en validar_factura: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Error interno del servidor',
            'error': str(e)
        }), 500

@facturas_bp.route('/health', methods=['GET'])
def health_check():
    """
    Endpoint para verificar que el servicio está funcionando
    """
    return jsonify({
        'success': True,
        'message': 'Servicio de facturas operativo',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    }), 200

# @facturas_bp.route('/crear', methods=['POST'])
# def crear_factura():
#     """
#     Endpoint para crear una nueva factura
#     """
#     try:
#         if not request.is_json:
#             return jsonify({'success': False, 'message': 'Se esperaba JSON'}), 400
        
#         datos = request.get_json()
        
#         # Validar primero
#         #es_valido, resultado_validacion, errores = validar_json_factura(datos)
        
#         # if not es_valido:
#         #     return jsonify({
#         #         'success': False,
#         #         'message': 'Datos de factura inválidos',
#         #         'errors': errores
#         #     }), 422
        
#         # Aquí iría la lógica para guardar en base de datos
#         # Por ejemplo:
#         # factura_guardada = guardar_factura_en_bd(resultado_validacion)
        
#         # Simular guardado exitoso
#         factura_guardada = {
#             'id': 12345,
#             'fecha_creacion': datetime.now().isoformat(),
#             'estado': 'pendiente',
#             'datos': resultado_validacion
#         }
        
#         return jsonify({
#             'success': True,
#             'message': 'Factura creada exitosamente',
#             'data': factura_guardada
#         }), 201
        
#     except Exception as e:
#         logger.error(f"Error en crear_factura: {str(e)}")
#         return jsonify({
#             'success': False,
#             'message': 'Error al crear factura',
#             'error': str(e)
#         }), 500


# # ============================================
# # RUTAS PARA CLIENTES
# # ============================================

# @facturas_bp.route('/clientes/validar', methods=['POST'])
# def validar_cliente():
#     """
#     Endpoint para validar solo los datos de un cliente
#     """
#     try:
#         if not request.is_json:
#             return jsonify({'success': False, 'message': 'Se esperaba JSON'}), 400
        
#         datos = request.get_json()
        
#         # Validar solo cliente
#         schema = ClienteSchema()
#         cliente_validado = schema.load(datos)
        
#         return jsonify({
#             'success': True,
#             'message': 'Cliente válido',
#             'data': cliente_validado
#         }), 200
        
#     except ValidationError as e:
#         return jsonify({
#             'success': False,
#             'message': 'Cliente inválido',
#             'errors': e.messages
#         }), 422
#     except Exception as e:
#         return jsonify({'success': False, 'error': str(e)}), 500


# @facturas_bp.route('/clientes/<int:cliente_id>', methods=['GET'])
# def obtener_cliente(cliente_id):
#     """
#     Endpoint para obtener un cliente por ID
#     """
#     try:
#         # Aquí iría la lógica para buscar en BD
#         # cliente = buscar_cliente_por_id(cliente_id)
        
#         # Datos de ejemplo
#         cliente_ejemplo = {
#             'id': cliente_id,
#             'cli_documento': '12345678',
#             'cli_nombres': 'Juan Pérez',
#             'cli_telefono': '77712345',
#             'cli_direccion': 'Av. Principal #123'
#         }
        
#         return jsonify({
#             'success': True,
#             'data': cliente_ejemplo
#         }), 200
        
#     except Exception as e:
#         return jsonify({'success': False, 'error': str(e)}), 500


# # ============================================
# # RUTAS PARA FORMAS DE PAGO
# # ============================================

# @facturas_bp.route('/formas-pago/validar', methods=['POST'])
# def validar_forma_pago():
#     """
#     Endpoint para validar una forma de pago
#     """
#     try:
#         if not request.is_json:
#             return jsonify({'success': False, 'message': 'Se esperaba JSON'}), 400
        
#         datos = request.get_json()
        
#         # Validar forma de pago
#         schema = FormaPagoSchema()
#         forma_pago_validada = schema.load(datos)
        
#         return jsonify({
#             'success': True,
#             'message': 'Forma de pago válida',
#             'data': forma_pago_validada
#         }), 200
        
#     except ValidationError as e:
#         return jsonify({
#             'success': False,
#             'message': 'Forma de pago inválida',
#             'errors': e.messages
#         }), 422
#     except Exception as e:
#         return jsonify({'success': False, 'error': str(e)}), 500


# @facturas_bp.route('/formas-pago', methods=['GET'])
# def listar_formas_pago():
#     """
#     Endpoint para listar todas las formas de pago disponibles
#     """
#     try:
#         # Datos de ejemplo - en producción vendrían de BD
#         formas_pago = [
#             {'codigo': '01', 'descripcion': 'Efectivo'},
#             {'codigo': '02', 'descripcion': 'Tarjeta de crédito'},
#             {'codigo': '03', 'descripcion': 'Tarjeta de débito'},
#             {'codigo': '04', 'descripcion': 'Transferencia bancaria'},
#             {'codigo': '05', 'descripcion': 'Cheque'}
#         ]
        
#         return jsonify({
#             'success': True,
#             'data': formas_pago
#         }), 200
        
#     except Exception as e:
#         return jsonify({'success': False, 'error': str(e)}), 500


# # ============================================
# # RUTAS PARA DETALLE DE FACTURA
# # ============================================

# @facturas_bp.route('/detalle/validar', methods=['POST'])
# def validar_detalle():
#     """
#     Endpoint para validar un item del detalle de factura
#     """
#     try:
#         if not request.is_json:
#             return jsonify({'success': False, 'message': 'Se esperaba JSON'}), 400
        
#         datos = request.get_json()
        
#         # Validaciones básicas para detalle
#         errores = []
        
#         if 'producto' not in datos or not datos['producto']:
#             errores.append('El producto es obligatorio')
        
#         if 'cantidad' not in datos:
#             errores.append('La cantidad es obligatoria')
#         elif not isinstance(datos['cantidad'], (int, float)) or datos['cantidad'] <= 0:
#             errores.append('La cantidad debe ser un número positivo')
        
#         if 'precio' not in datos:
#             errores.append('El precio es obligatorio')
#         elif not isinstance(datos['precio'], (int, float)) or datos['precio'] <= 0:
#             errores.append('El precio debe ser un número positivo')
        
#         if errores:
#             return jsonify({
#                 'success': False,
#                 'message': 'Detalle inválido',
#                 'errors': errores
#             }), 422
        
#         return jsonify({
#             'success': True,
#             'message': 'Detalle válido',
#             'data': datos
#         }), 200
        
#     except Exception as e:
#         return jsonify({'success': False, 'error': str(e)}), 500


# # ============================================
# # RUTAS DE CONSULTA GENERAL
# # ============================================

# @facturas_bp.route('/<int:factura_id>', methods=['GET'])
# def obtener_factura(factura_id):
#     """
#     Endpoint para obtener una factura específica por ID
#     """
#     try:
#         # Aquí iría la lógica para buscar en BD
#         # factura = buscar_factura_por_id(factura_id)
        
#         # Datos de ejemplo
#         factura_ejemplo = {
#             'id': factura_id,
#             'numero': f'FAC-{factura_id:05d}',
#             'fecha': datetime.now().isoformat(),
#             'cliente': {
#                 'cli_documento': '12345678',
#                 'cli_nombres': 'Juan Pérez'
#             },
#             'total': 1500.50,
#             'estado': 'emitida'
#         }
        
#         return jsonify({
#             'success': True,
#             'data': factura_ejemplo
#         }), 200
        
#     except Exception as e:
#         return jsonify({'success': False, 'error': str(e)}), 500


# @facturas_bp.route('/', methods=['GET'])
# @facturas_bp.route('', methods=['GET'])
# def listar_facturas():
#     """
#     Endpoint para listar todas las facturas (con paginación opcional)
#     """
#     try:
#         # Parámetros de paginación
#         pagina = request.args.get('pagina', 1, type=int)
#         limite = request.args.get('limite', 10, type=int)
        
#         # Aquí iría la lógica para buscar en BD con paginación
#         # facturas = buscar_facturas(offset=(pagina-1)*limite, limit=limite)
        
#         # Datos de ejemplo
#         facturas = [
#             {'id': 1, 'numero': 'FAC-00001', 'fecha': '2024-01-01', 'total': 1500.50},
#             {'id': 2, 'numero': 'FAC-00002', 'fecha': '2024-01-02', 'total': 2300.00},
#             {'id': 3, 'numero': 'FAC-00003', 'fecha': '2024-01-03', 'total': 890.75},
#         ]
        
#         return jsonify({
#             'success': True,
#             'data': facturas,
#             'paginacion': {
#                 'pagina': pagina,
#                 'limite': limite,
#                 'total': len(facturas)
#             }
#         }), 200
        
#     except Exception as e:
#         return jsonify({'success': False, 'error': str(e)}), 500


# # ============================================
# # RUTAS DE ESTADÍSTICAS
# # ============================================

# @facturas_bp.route('/estadisticas', methods=['GET'])
# def obtener_estadisticas():
#     """
#     Endpoint para obtener estadísticas de facturación
#     """
#     try:
#         # Datos de ejemplo
#         estadisticas = {
#             'total_facturas': 150,
#             'total_ventas': 125000.50,
#             'facturas_por_mes': {
#                 'enero': 45,
#                 'febrero': 52,
#                 'marzo': 53
#             },
#             'forma_pago_mas_usada': '01 - Efectivo',
#             'promedio_por_factura': 833.34
#         }
        
#         return jsonify({
#             'success': True,
#             'data': estadisticas
#         }), 200
        
#     except Exception as e:
#         return jsonify({'success': False, 'error': str(e)}), 500


# # ============================================
# # RUTA DE HEALTH CHECK
# # ============================================

# @facturas_bp.route('/health', methods=['GET'])
# def health_check():
#     """
#     Endpoint para verificar que el servicio está funcionando
#     """
#     return jsonify({
#         'success': True,
#         'message': 'Servicio de facturas operativo',
#         'timestamp': datetime.now().isoformat(),
#         'version': '1.0.0'
#     }), 200


# # ============================================
# # MANEJADORES DE ERRORES DEL BLUEPRINT
# # ============================================

# @facturas_bp.errorhandler(404)
# def not_found(error):
#     """Manejador para rutas no encontradas"""
#     return jsonify({
#         'success': False,
#         'message': 'Recurso no encontrado',
#         'error': 'La ruta solicitada no existe'
#     }), 404

# @facturas_bp.errorhandler(405)
# def method_not_allowed(error):
#     """Manejador para métodos no permitidos"""
#     return jsonify({
#         'success': False,
#         'message': 'Método no permitido',
#         'error': f'El método {request.method} no está permitido para esta ruta'
#     }), 405

# @facturas_bp.errorhandler(500)
# def internal_error(error):
#     """Manejador para errores internos"""
#     logger.error(f"Error interno: {str(error)}")
#     return jsonify({
#         'success': False,
#         'message': 'Error interno del servidor',
#         'error': 'Ha ocurrido un error inesperado'
#     }), 500