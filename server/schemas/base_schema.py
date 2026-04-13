# server/schemas/base_schema.py
from marshmallow import Schema, ValidationError
from datetime import datetime


class BaseSchema(Schema):
    """Schema base con validaciones comunes"""
    
    def handle_error(self, error, data, **kwargs):
        """Manejo personalizado de errores"""
        raise ValidationError(error.messages)
    
    @staticmethod
    def validate_fecha(value):
        """Valida formato de fecha"""
        if isinstance(value, str):
            try:
                datetime.fromisoformat(value.replace('Z', '+00:00'))
            except ValueError:
                raise ValidationError("Formato de fecha inválido. Use ISO format")