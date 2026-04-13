# server/routes/notas_credito.py
"""
Rutas para notas de crédito
"""
from flask import Blueprint, request, jsonify
from server.controllers.nota_credito_controller import NotaCreditoController
from server.utils.response_builder import ResponseBuilder, send_response

notas_credito_bp = Blueprint('notas_credito', __name__, url_prefix='/notas-credito')

# Instanciar controlador
nota_credito_controller = NotaCreditoController()


def handle_request(controller_func):
    """Helper para manejar solicitudes JSON"""
    if not request.is_json:
        return send_response(ResponseBuilder.error('Se requiere JSON', status_code=400))
    
    datos = request.get_json()
    respuesta, error, status_code = controller_func(datos)
    return jsonify(respuesta), status_code


@notas_credito_bp.route('/validar', methods=['POST'])
def validar_nota_credito():
    """Valida una nota de crédito"""
    return handle_request(nota_credito_controller.validar_controller)


@notas_credito_bp.route('/procesar', methods=['POST'])
def procesar_nota_credito():
    """Procesa una nota de crédito"""
    return handle_request(nota_credito_controller.procesar_controller)


@notas_credito_bp.route('/armar', methods=['POST'])
def armar_nota_credito():
    """Arma/estructura una nota de crédito"""
    return handle_request(nota_credito_controller.armar_controller)


@notas_credito_bp.route('/health', methods=['GET'])
def health_check():
    """Health check"""
    respuesta, status_code = nota_credito_controller.health_check_controller()
    return jsonify(respuesta), status_code