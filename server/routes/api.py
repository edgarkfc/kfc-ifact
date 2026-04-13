# server/routes/api.py
from flask import Blueprint, request, jsonify
from server.controllers.bills_controller import (    
    procesar_factura_controller,    
)
from server.controllers.notas_credito_module import (    
    procesar_nota_credito_controller,    
)

# Blueprint para facturas
facturas_bp = Blueprint('facturas', __name__, url_prefix='/api/facturas')

# Blueprint para notas de crédito
notas_credito_bp = Blueprint('notas_credito', __name__, url_prefix='/api/notas-credito')


def handle_request(controller_func):
    """Helper para manejar solicitudes JSON de manera uniforme"""
    if not request.is_json:
        return jsonify({'success': False, 'message': 'Se requiere JSON'}), 400
    
    datos = request.get_json()
    respuesta, error, status_code = controller_func(datos)
    return jsonify(respuesta), status_code


# ============================================
# RUTAS PARA FACTURAS - SOLO PROCESAR
# ============================================

@facturas_bp.route('/procesar', methods=['POST'])
def procesar_factura_endpoint():
    return handle_request(procesar_factura_controller)



# ============================================
# RUTAS PARA NOTAS DE CRÉDITO - SOLO PROCESAR
# ============================================

@notas_credito_bp.route('/procesar', methods=['POST'])
def procesar_nota_credito_endpoint():
    return handle_request(procesar_nota_credito_controller)

