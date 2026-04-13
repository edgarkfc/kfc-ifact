# server/schemas/componentes.py
"""
Componentes de schemas reutilizables
Migrado desde validators.py
"""
from marshmallow import Schema, fields, validates, ValidationError, validates_schema, EXCLUDE, pre_load, post_load, validate  # ← Agregar 'validate'
import logging

logger = logging.getLogger(__name__)

TOLERANCIA = 0.05


class FormaPagoSchema(Schema):
    """Schema para forma de pago"""
    class Meta:
        unknown = EXCLUDE

    formapagoactura_id = fields.Str(required=False, allow_none=True)
    formapago_id = fields.Str(required=True)
    cfac_id = fields.Str(required=False, allow_none=True)
    fpf_total_pagar = fields.Float(required=True)
    formapago = fields.Str(required=True)
    
    @validates('fpf_total_pagar')
    def validate_fpf_total_pagar(self, value, **kwargs):
        if value <= 0:
            raise ValidationError('El total a pagar debe ser mayor a 0')
        if value > 99999999.99:
            raise ValidationError('El total a pagar no puede ser mayor a 99999999.99')
        
        str_value = f"{value:.10f}".rstrip('0')
        if '.' in str_value:
            decimales = str_value.split('.')[-1]
            if len(decimales) > 3:
                raise ValidationError(f'Máximo 3 decimales permitidos (tiene {len(decimales)})')
    
    @validates('formapago')
    def validate_formapago_varchar4(self, value, **kwargs):
        if not isinstance(value, str):
            raise ValidationError('El campo debe ser un texto')
        if not (len(value) == 2 and value.isdigit()):
            raise ValidationError('El metodo de pago debe contener exactamente 2 dígitos numéricos')
        numero = int(value)
        if numero < 1 or numero > 23:
            raise ValidationError('Metodo de pago no registrado, debe estar entre 01 y 23')


class DetalleFacturaSchema(Schema):
    """Schema para detalle de factura"""
    class Meta:
        unknown = EXCLUDE
    
    detallefactura_id = fields.Str(required=True)
    dtfacplu_id = fields.Int(required=True)   
    dtfac_cantidad = fields.Float(
        required=True, 
        validate=validate.Range(min=0, error="La cantidad debe ser mayor a 0"),
        error_messages={"required": "La cantidad es obligatoria", "invalid": "Cantidad inválida"}
    )    
    dtfac_precio_unitario = fields.Float(
        required=True, 
        validate=validate.Range(min=0, error="El precio unitario debe ser mayor a 0"),
        error_messages={"required": "El precio unitario es obligatorio"}
    )    
    dtfac_iva = fields.Float(required=True, allow_none=True)    
    dtfac_total = fields.Float(
        required=True, 
        validate=validate.Range(min=0, error="El total debe ser mayor a 0"),
        error_messages={"required": "El total es obligatorio"}
    )
    aplicaImpuesto1 = fields.Int(required=False, allow_none=True)
    aplicaImpuesto2 = fields.Int(required=False, allow_none=True)
    aplicaImpuesto3 = fields.Int(required=False, allow_none=True)
    aplicaImpuesto4 = fields.Int(required=False, allow_none=True)
    aplicaImpuesto5 = fields.Int(required=False, allow_none=True)
    dtfac_valor_descuento = fields.Float(
        required=True, 
        validate=validate.Range(min=0, error="El valor del descuento debe ser mayor o igual a 0"),
        error_messages={"required": "El valor del descuento es obligatorio"}
    )
    dtfac_porcentaje_descuento = fields.Int(
        required=True, 
        validate=validate.Range(
            min=0, 
            max=100, 
            error="El porcentaje de descuento debe estar entre 0% y 100%"
        ),
        error_messages={
            "required": "El porcentaje de descuento es obligatorio",
            "invalid": "El porcentaje debe ser un número entero",
            "null": "El porcentaje no puede ser nulo"
        }
    )
    dtfac_totaldesc = fields.Float(required=False, allow_none=True)
    dtfac_ivadesc = fields.Float(required=False, allow_none=True)
    dtfac_descripcion = fields.Str(required=True)
    
    @validates_schema
    def validate_descuentos(self, data, **kwargs):
        """Valida la consistencia entre descuentos por porcentaje y valor"""
        cantidad = data.get('dtfac_cantidad', 0)
        precio_unitario = data.get('dtfac_precio_unitario', 0)
        total_declarado = data.get('dtfac_total', 0)
        
        if precio_unitario == 0:
            return
        
        subtotal_original = cantidad * precio_unitario
        
        if abs(total_declarado - subtotal_original) > TOLERANCIA:
            valor_descuento = data.get('dtfac_valor_descuento', 0)
            if valor_descuento > 0:
                total_con_descuento = subtotal_original - valor_descuento
                if abs(total_declarado - total_con_descuento) > TOLERANCIA:
                    raise ValidationError(
                        f'Total inconsistente para producto {data.get("dtfac_descripcion", "desconocido")}: '
                        f'esperado={total_con_descuento:.2f} (con descuento), declarado={total_declarado:.2f}'
                    )
            else:
                raise ValidationError(
                    f'Total inconsistente para producto {data.get("dtfac_descripcion", "desconocido")}: '
                    f'calculado={subtotal_original:.2f}, declarado={total_declarado:.2f}'
                )


class ClienteSchema(Schema):
    """Schema para cliente"""
    class Meta:
        unknown = EXCLUDE
    
    cliente_id = fields.Str(required=False, allow_none=True)
    cliente_documento = fields.Str(
        required=True, 
        validate=validate.Length(min=1, error="El documento del cliente no puede estar vacío"),
        error_messages={"required": "El documento del cliente es obligatorio"}
    )
    cliente_nombres = fields.Str(
        required=True, 
        validate=validate.Length(min=1, error="Los nombres del cliente no pueden estar vacíos"),
        error_messages={"required": "Los nombres del cliente son obligatorios"}
    )
    cliente_apellidos = fields.Str(required=False, allow_none=True)
    cliente_telefono = fields.Str(required=True)
    cliente_direccion = fields.Str(required=False, allow_none=True)
    cliente_email = fields.Str(required=False, allow_none=True)    
    
    @pre_load
    def clean_cli_direccion(self, data, **kwargs):
        """Convierte string 'null' a None"""
        if 'cliente_direccion' in data and data['cliente_direccion'] == 'null':
            data['cliente_direccion'] = None
        return data
    
    @validates('cliente_documento')
    def validate_cliente_documento(self, value, **kwargs):
        if value is None or (isinstance(value, str) and value.strip() == ''):
            raise ValidationError('El documento del cliente no puede estar vacío')
        if isinstance(value, str) and value.lower() == 'null':
            raise ValidationError('El documento del cliente no puede ser "null"')
    
    @validates('cliente_nombres')
    def validate_cliente_nombres(self, value, **kwargs):
        if value is None or (isinstance(value, str) and value.strip() == ''):
            raise ValidationError('Los nombres del cliente no pueden estar vacíos')
        if isinstance(value, str) and value.lower() == 'null':
            raise ValidationError('Los nombres del cliente no pueden ser "null"')
    
    @validates_schema
    def validate_required_fields(self, data, **kwargs):
        documento = data.get('cliente_documento')
        if not documento or (isinstance(documento, str) and documento.strip() == ''):
            raise ValidationError({'cliente_documento': 'El documento del cliente es obligatorio y no puede estar vacío'})
        
        nombres = data.get('cliente_nombres')
        if not nombres or (isinstance(nombres, str) and nombres.strip() == ''):
            raise ValidationError({'cliente_nombres': 'Los nombres del cliente son obligatorios y no pueden estar vacíos'})


class CabeceraFacturaSchema(Schema):
    """Schema para cabecera de factura"""
    class Meta:
        unknown = EXCLUDE
    
    cabfact_id = fields.Str(
        required=True, 
        allow_none=False,
        error_messages={
            "required": "El ID de la factura es obligatorio",
            "null": "El ID de la factura no puede ser nulo",
            "invalid": "El ID de la factura no puede estar vacío"
        }
    )
    cabfact_nrofact_nc = fields.Str(required=False, allow_none=True)
    delivery_id = fields.Str(required=False)
    cabfact_fechacreacion = fields.Str(required=True)
    cabfact_subtotal = fields.Float(required=True)    
    cabfact_iva = fields.Float(required=True)
    cabfact_total = fields.Float(required=True)
    cabfact_valor_descuento = fields.Float(required=False, allow_none=True)    
    cabfact_porcentaje_descuento = fields.Int(
        required=False,
        allow_none=True,
        validate=validate.Range(min=0, max=100, error="El porcentaje debe estar entre 0 y 100")
    )
    cabfact_cajero = fields.Str(required=False, allow_none=True)
    cabfact_tasa_conversion = fields.Float(required=True)
    
    @pre_load
    def set_default_descuento(self, data, **kwargs):
        if 'cabfact_valor_descuento' not in data or data['cabfact_valor_descuento'] is None:
            data['cabfact_valor_descuento'] = 0
        if 'cabfact_porcentaje_descuento' not in data or data['cabfact_porcentaje_descuento'] is None:
            data['cabfact_porcentaje_descuento'] = 0
        return data
    
    @validates('cabfact_id')
    def validate_cabfact_id(self, value, **kwargs):
        if value is None:
            raise ValidationError('El ID de la factura no puede ser nulo')
        if isinstance(value, str) and value.strip() == '':
            raise ValidationError('El ID de la factura no puede estar vacío')
        if isinstance(value, str) and value.lower() == 'null':
            raise ValidationError('El ID de la factura no puede ser "null"')
    
    @validates_schema
    def validate_cabecera(self, data, **kwargs):
        subtotal = data.get('cabfact_subtotal', 0)
        descuento_valor = data.get('cabfact_valor_descuento', 0)
        iva_declarado = data.get('cabfact_iva', 0)
        total_declarado = data.get('cabfact_total', 0)
        
        total_calculado = subtotal + iva_declarado
        
        if abs(total_calculado - total_declarado) > TOLERANCIA:
            total_con_descuento = subtotal + iva_declarado - descuento_valor
            if abs(total_con_descuento - total_declarado) <= TOLERANCIA:
                logger.debug(f"Descuento aplicado después del IVA: {descuento_valor:.2f}")
            else:
                raise ValidationError(
                    f'El total calculado ({total_calculado:.2f}) o con descuento ({total_con_descuento:.2f}) '
                    f'no coincide con el declarado ({total_declarado:.2f})'
                )


class RestauranteSchema(Schema):
    """Schema para restaurante"""
    class Meta:
        unknown = EXCLUDE
    
    restaurante = fields.Str(required=True)
    rest_id = fields.Int(required=True)
    impuesto_rest = fields.Bool(required=True, allow_none=False)
    nro_estacion = fields.Int(required=True)   


class ConfigImpresoraSchema(Schema):
    """Schema para configuración de impresora"""
    class Meta:
        unknown = EXCLUDE
    
    impresion_qr = fields.Bool(required=True, allow_none=False)
    impresion_msgqr = fields.Bool(required=True, allow_none=False)
    impresion_cupon = fields.Bool(required=True, allow_none=False)
    
    @post_load
    def log_config(self, data, **kwargs):
        logger.debug(f"ConfigImpresoraSchema procesado: {data}")
        return data