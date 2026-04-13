# server/utils/response_builder.py
"""
Constructor estandarizado de respuestas JSON
"""
from datetime import datetime
from typing import Dict, Any, Optional, Tuple, Union
from flask import jsonify

class ResponseBuilder:
    """Construye respuestas estandarizadas para la API"""
    
    @staticmethod
    def success(
        data: Any = None, 
        message: str = "Operación exitosa", 
        status_code: int = 200,
        metadata: Dict = None
    ) -> Tuple[Dict, int]:
        """Respuesta exitosa"""
        response = {
            'success': True,
            'message': message,
            'timestamp': datetime.now().isoformat(),
        }
        
        if data is not None:
            response['data'] = data
            
        if metadata:
            response['metadata'] = metadata
            
        return response, status_code
    
    @staticmethod
    def error(
        message: str, 
        errors: Any = None, 
        status_code: int = 400,
        error_code: str = None
    ) -> Tuple[Dict, int]:
        """Respuesta de error"""
        response = {
            'success': False,
            'message': message,
            'timestamp': datetime.now().isoformat()
        }
        
        if errors:
            response['errors'] = errors
            
        if error_code:
            response['error_code'] = error_code
            
        return response, status_code
    
    @staticmethod
    def validation_error(errors: Dict) -> Tuple[Dict, int]:
        """Error de validación específico (422)"""
        return ResponseBuilder.error(
            message="Error de validación",
            errors=errors,
            status_code=422,
            error_code="VALIDATION_ERROR"
        )
    
    @staticmethod
    def not_found(resource: str) -> Tuple[Dict, int]:
        """Recurso no encontrado (404)"""
        return ResponseBuilder.error(
            message=f"{resource} no encontrado",
            status_code=404,
            error_code="NOT_FOUND"
        )
    
    @staticmethod
    def internal_error(error: str = None) -> Tuple[Dict, int]:
        """Error interno del servidor (500)"""
        return ResponseBuilder.error(
            message="Error interno del servidor",
            errors=error if error else "Contacte al administrador",
            status_code=500,
            error_code="INTERNAL_ERROR"
        )

def send_response(response_tuple):
    """Helper para usar en routes - convierte tupla a Flask response"""
    return jsonify(response_tuple[0]), response_tuple[1]