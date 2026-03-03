# validators/factura_validator.py
from marshmallow import Schema, fields, validates, ValidationError, validates_schema, EXCLUDE, RAISE
import re

class FormaPagoSchema(Schema):
    class Meta:
        # INCLUDE: incluye campos desconocidos en el output
        # EXCLUDE: excluye campos desconocidos (los ignora)
        # RAISE: lanza error si hay campos desconocidos (default)
        unknown = EXCLUDE  # Ignora campos no definidos

    fpf_total_pagar = fields.Float(
        required=True,       
        validate=lambda x: x > 0,
        error_messages={
            'required': 'El total a pagar es obligatorio.',
            'invalid': 'El total a pagar debe ser un número.',
            'validator_failed': 'El total a pagar debe ser mayor a 0.'
        }
    )
    
    Formapago_FacturaVarchar4 = fields.Str(
        required=True,        
        validate=lambda x: len(x) == 2 and x.isdigit(),
        error_messages={
            'required': 'El campo Formapago_FacturaVarchar4 es obligatorio.',
            'invalid': 'El campo debe tener exactamente 2 dígitos numéricos.',
            'validator_failed': 'Solo se permiten 2 dígitos numéricos.'
        }
    )
    
    #@validates('fpf_total_pagar')
    def validate_fpf_total_pagar(self, value):
        if value > 99999999.99:
            raise ValidationError('El total a pagar no puede ser mayor a 99999999.99')
        # Validar hasta 3 decimales
        str_value = str(value)
        if '.' in str_value:
            decimales = str_value.split('.')[-1]
            if len(decimales) > 3:
                raise ValidationError('Máximo 3 decimales permitidos')
        # También validar notación científica
        elif 'e' in str_value.lower():
            # Si viene en notación científica, convertir a float y formatear
            formatted = f"{value:.10f}".rstrip('0').rstrip('.')
            if '.' in formatted:
                decimales = formatted.split('.')[-1]
                if len(decimales) > 3:
                    raise ValidationError('Máximo 3 decimales permitidossss')

class FacturaSchema(Schema):
    factura = fields.Dict(
        required=True,
        error_messages={
            'required': 'El json no es valido en su estructura'
        }
    )
    
    @validates_schema
    def validate_factura_structure(self, data, **kwargs):
        factura = data.get('factura', {})
        errores = []
        
        # Validar campos requeridos
        campos_requeridos = ['cliente', 'detalle_factura', 'formas_pago']
        for campo in campos_requeridos:
            if campo not in factura:
                errores.append(f'La llave "{campo}" no está en el JSON')
        
        # Si falta algún campo, no continuar con validaciones específicas
        if errores:
            raise ValidationError(errores)
        
        # Validar cliente
        if not isinstance(factura['cliente'], dict):
            errores.append('El cliente debe ser un objeto')
        if 'cli_documento' not in factura['cliente']:
            errores.append('El campo "cli_documento" es obligatorio')
        if 'cli_nombres' not in factura['cliente']:
            errores.append('El campo "cli_nombres" es obligatorio')
        if 'cli_telefono' not in factura['cliente']:
            errores.append('El campo "cli_telefono" es obligatorio')
        if 'cli_direccion' not in factura['cliente']:
            errores.append('El campo "cli_direccion" es obligatorio')
        cli_documento = factura['cliente']['cli_documento']
        if not cli_documento or len(cli_documento.strip()) == 0:
            errores.append('El documento del cliente no puede estar vacío')
        cli_nombres = factura['cliente']['cli_nombres']
        if not cli_nombres or len(cli_nombres.strip()) == 0:
            errores.append('Los nombres del cliente no pueden estar vacíos')
        cli_telefono = factura['cliente']['cli_telefono']
        if not cli_telefono or len(cli_telefono.strip()) == 0:
            errores.append('El teléfono del cliente no puede estar vacío')
        cli_direccion = factura['cliente']['cli_direccion']
        if not cli_direccion or len(cli_direccion.strip()) == 0:
            errores.append('La dirección del cliente no puede estar vacía')                 
        
        # Validar detalle_factura
        if not isinstance(factura['detalle_factura'], list):
            errores.append('El detalle debe ser un array')
        elif len(factura['detalle_factura']) == 0:
            errores.append('Debe haber al menos un detalle de factura')
        
        # Validar formas_pago
        if not isinstance(factura['formas_pago'], list):
            errores.append('El campo formas_pago debe ser un arreglo.')
        elif len(factura['formas_pago']) < 1:
            errores.append('Debe haber al menos una forma de pago.')
        elif len(factura['formas_pago']) > 1:
            # Validar cada forma de pago
            
            for i, fp in enumerate(factura['formas_pago']):
                try:
                    # Validar que fp sea diccionario
                    print(f"Validando forma_pago[{i}]: {fp}")
                    if not isinstance(fp, dict):
                        errores.append(f'formas_pago[{i}]: debe ser un objeto')
                        continue
                    forma_pago_schema = FormaPagoSchema()
                    forma_pago_schema.load(fp)
                except ValidationError as e:
                    for field, msgs in e.messages.items():
                        errores.append(f"formas_pago[{i}].{field}: {msgs[0]}")
        
        if errores:
            raise ValidationError(errores)
        
    
        
        