# server/routes/facturas.py
"""
Rutas para facturas
"""
from flask import Blueprint, request, jsonify
from server.controllers.factura_controller import FacturaController
from server.utils.response_builder import ResponseBuilder, send_response

facturas_bp = Blueprint('facturas', __name__, url_prefix='/facturas')

# Instanciar controlador
factura_controller = FacturaController()


def handle_request(controller_func):
    """Helper para manejar solicitudes JSON"""
    if not request.is_json:
        return send_response(ResponseBuilder.error('Se requiere JSON', status_code=400))
    
    datos = request.get_json()
    respuesta, error, status_code = controller_func(datos)
    return jsonify(respuesta), status_code


@facturas_bp.route('/validar', methods=['POST'])
def validar_factura():
    """Valida una factura"""
    return handle_request(factura_controller.validar_controller)


@facturas_bp.route('/procesar', methods=['POST'])
def procesar_factura():
    """Procesa una factura"""
    return handle_request(factura_controller.procesar_controller)


@facturas_bp.route('/armar', methods=['POST'])
def armar_factura():
    """Arma/estructura una factura"""
    return handle_request(factura_controller.armar_controller)


@facturas_bp.route('/health', methods=['GET'])
def health_check():
    """Health check"""
    respuesta, status_code = factura_controller.health_check_controller()
    return jsonify(respuesta), status_code