# routes/api.py
from flask import Blueprint, request, jsonify
from server.controllers.bills_controller import (
    validar_factura_controller,
    procesar_factura_controller,
    armar_factura_controller,
    health_check_controller
)

facturas_bp = Blueprint('facturas', __name__, url_prefix='/api/facturas')

def handle_request(controller_func):
    """Helper para manejar solicitudes JSON de manera uniforme"""
    if not request.is_json:
        return jsonify({'success': False, 'message': 'Se requiere JSON'}), 400
    
    datos = request.get_json()
    respuesta, error, status_code = controller_func(datos)
    return jsonify(respuesta), status_code

@facturas_bp.route('/validar', methods=['POST'])
def validar_factura_endpoint():
    return handle_request(validar_factura_controller)

@facturas_bp.route('/procesar', methods=['POST'])
def procesar_factura_endpoint():
    return handle_request(procesar_factura_controller)

@facturas_bp.route('/armar', methods=['POST'])
def armar_factura_endpoint():
    return handle_request(armar_factura_controller)

@facturas_bp.route('/health', methods=['GET'])
def health_check():
    respuesta, status_code = health_check_controller()
    return jsonify(respuesta), status_code