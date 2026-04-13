# server/controllers/helpers/validators.py
from marshmallow import Schema, fields, validates, ValidationError, validates_schema, EXCLUDE, pre_load, post_load, validate
import logging
from decimal import Decimal, ROUND_HALF_UP

logger = logging.getLogger(__name__)

# ============================================
# CONSTANTES
# ============================================
TOLERANCIA = 0.05  # Tolerancia de 5 centésimas para errores de redondeo

# ============================================
# SCHEMA FORMA DE PAGO
# ============================================
class FormaPagoSchema(Schema):
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
        
        # Validar decimales (máximo 3)
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


# ============================================
# SCHEMA DETALLE FACTURA
# ============================================
class DetalleFacturaSchema(Schema):
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
        
        # Si el precio unitario es 0, no validamos (productos complementarios)
        if precio_unitario == 0:
            return
        
        # Calcular subtotal CON IVA incluido
        subtotal_original = cantidad * precio_unitario
        
        # Validar que el total declarado sea consistente
        if abs(total_declarado - subtotal_original) > TOLERANCIA:
            # Si hay descuento por producto, podría ser diferente
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


# ============================================
# SCHEMA CLIENTE
# ============================================
class ClienteSchema(Schema):
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
        """Valida que el documento no sea None, null o cadena vacía"""
        if value is None or (isinstance(value, str) and value.strip() == ''):
            raise ValidationError('El documento del cliente no puede estar vacío')
        if isinstance(value, str) and value.lower() == 'null':
            raise ValidationError('El documento del cliente no puede ser "null"')
    
    @validates('cliente_nombres')
    def validate_cliente_nombres(self, value, **kwargs):
        """Valida que los nombres no sean None, null o cadena vacía"""
        if value is None or (isinstance(value, str) and value.strip() == ''):
            raise ValidationError('Los nombres del cliente no pueden estar vacíos')
        if isinstance(value, str) and value.lower() == 'null':
            raise ValidationError('Los nombres del cliente no pueden ser "null"')
    
    @validates_schema
    def validate_required_fields(self, data, **kwargs):
        """Validación adicional para asegurar que los campos obligatorios no estén vacíos"""
        # Validar cliente_documento
        documento = data.get('cliente_documento')
        if not documento or (isinstance(documento, str) and documento.strip() == ''):
            raise ValidationError({'cliente_documento': 'El documento del cliente es obligatorio y no puede estar vacío'})
        
        # Validar cliente_nombres
        nombres = data.get('cliente_nombres')
        if not nombres or (isinstance(nombres, str) and nombres.strip() == ''):
            raise ValidationError({'cliente_nombres': 'Los nombres del cliente son obligatorios y no pueden estar vacíos'})


# server/controllers/helpers/validators.py
# ============================================
# SCHEMA CABECERA FACTURA
# ============================================
class CabeceraFacturaSchema(Schema):
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
        """Establece valores por defecto para los campos de descuento"""
        if 'cabfact_valor_descuento' not in data or data['cabfact_valor_descuento'] is None:
            data['cabfact_valor_descuento'] = 0
        if 'cabfact_porcentaje_descuento' not in data or data['cabfact_porcentaje_descuento'] is None:
            data['cabfact_porcentaje_descuento'] = 0
        return data
    
    @validates('cabfact_id')
    def validate_cabfact_id(self, value, **kwargs):
        """Valida que cabfact_id no esté vacío, nulo o sea string vacío"""
        if value is None:
            raise ValidationError('El ID de la factura no puede ser nulo')
        if isinstance(value, str) and value.strip() == '':
            raise ValidationError('El ID de la factura no puede estar vacío')
        if isinstance(value, str) and value.lower() == 'null':
            raise ValidationError('El ID de la factura no puede ser "null"')
    
    @validates_schema
    def validate_cabecera(self, data, **kwargs):
        """
        Valida la consistencia de los cálculos en cabecera.
        El subtotal ya incluye el descuento aplicado.
        """
        subtotal = data.get('cabfact_subtotal', 0)
        descuento_valor = data.get('cabfact_valor_descuento', 0)
        iva_declarado = data.get('cabfact_iva', 0)
        total_declarado = data.get('cabfact_total', 0)
        
        # El total debe ser: subtotal + IVA - descuento_cabecera
        # Pero como el subtotal ya tiene el descuento aplicado? 
        # O el descuento se aplica después del IVA?
        # Por ahora, validamos que total = subtotal + IVA (ya que el descuento está en el subtotal)
        total_calculado = subtotal + iva_declarado
        
        # Validar total
        if abs(total_calculado - total_declarado) > TOLERANCIA:
            # Si no coincide, podría ser que el descuento se aplique después
            total_con_descuento = subtotal + iva_declarado - descuento_valor
            if abs(total_con_descuento - total_declarado) <= TOLERANCIA:
                # Si coincide con descuento aplicado después, está bien
                logger.debug(f"Descuento aplicado después del IVA: {descuento_valor:.2f}")
            else:
                raise ValidationError(
                    f'El total calculado ({total_calculado:.2f}) o con descuento ({total_con_descuento:.2f}) '
                    f'no coincide con el declarado ({total_declarado:.2f})'
                )

# ============================================
# SCHEMA RESTAURANTE
# ============================================
class RestauranteSchema(Schema):
    class Meta:
        unknown = EXCLUDE
    
    restaurante = fields.Str(required=True)
    rest_id = fields.Int(required=True)
    impuesto_rest = fields.Bool(required=True, allow_none=False)
    nro_estacion = fields.Int(required=True)   


# ============================================
# SCHEMA CONFIGURACION IMPRESORA
# ============================================
class ConfigImpresoraSchema(Schema):
    class Meta:
        unknown = EXCLUDE
    
    impresion_qr = fields.Bool(required=True, allow_none=False)
    impresion_msgqr = fields.Bool(required=True, allow_none=False)
    impresion_cupon = fields.Bool(required=True, allow_none=False)
    
    @post_load
    def log_config(self, data, **kwargs):
        logger.debug(f"=== ConfigImpresoraSchema procesado: {data} ===")
        return data


# ============================================
# SCHEMA FACTURA
# ============================================
class FacturaSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    restaurante = fields.Nested(RestauranteSchema, required=False)
    config_impresora = fields.Nested(ConfigImpresoraSchema, required=True)
    cabecera_factura = fields.Nested(CabeceraFacturaSchema, required=True)
    cliente = fields.Nested(ClienteSchema, required=True)
    detalle_factura = fields.List(fields.Nested(DetalleFacturaSchema), required=True)
    formas_pago = fields.List(fields.Nested(FormaPagoSchema), required=True)
    
    @pre_load
    def unwrap_factura(self, data, **kwargs):
        """Extrae el contenido de 'factura' si existe"""       
        logger.debug(f"Tipo de data: {type(data)}")
        logger.debug(f"Keys en data: {data.keys() if isinstance(data, dict) else 'No es dict'}")
        if isinstance(data, dict) and 'factura' in data:
            factura_data = data['factura']           
            logger.debug(f"Keys en factura: {factura_data.keys()}")
            logger.debug(f"config_impresora en factura: {factura_data.get('config_impresora')}")
            logger.debug(f"config_impresora type: {type(factura_data.get('config_impresora'))}")
            return factura_data
        logger.debug("=== No se encontró campo 'factura' ===")
        return data
    
    def _calcular_totales_detalle(self, detalle_items):
        """
        Calcula los totales del detalle de factura
        
        Returns:
            dict: {
                'subtotal_sin_iva': float,
                'total_iva': float,
                'total_con_iva': float
            }
        """
        subtotal_sin_iva = 0.0
        total_iva = 0.0
        total_con_iva = 0.0
        
        for item in detalle_items:
            cantidad = item.get('dtfac_cantidad', 0)
            precio_unitario = item.get('dtfac_precio_unitario', 0)
            iva_por_unidad = item.get('dtfac_iva', 0)
            total_declarado = item.get('dtfac_total', 0)
            
            # Si el precio es 0, es un producto complementario, lo ignoramos
            if precio_unitario == 0:
                continue
            
            # Usar el total declarado que ya incluye descuentos por producto
            item_total = total_declarado
            item_iva = cantidad * iva_por_unidad
            item_subtotal_sin_iva = item_total - item_iva
            
            subtotal_sin_iva += item_subtotal_sin_iva
            total_iva += item_iva
            total_con_iva += item_total
            
            logger.debug(f"Producto: {item.get('dtfac_descripcion')} - "
                        f"Total: {item_total:.2f}, "
                        f"IVA: {item_iva:.2f}, "
                        f"Subtotal sin IVA: {item_subtotal_sin_iva:.2f}")
        
        return {
            'subtotal_sin_iva': round(subtotal_sin_iva, 2),
            'total_iva': round(total_iva, 2),
            'total_con_iva': round(total_con_iva, 2)
        }
    
    def _round_to_2_decimals(self, value):
        """Redondea a 2 decimales usando el método HALF_UP"""
        return float(Decimal(str(value)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))
    
    @validates_schema
    def validate_cross_fields(self, data, **kwargs):
        """Validaciones que cruzan múltiples campos"""
        errores = []
        
        # Validar consistencia entre detalle y cabecera
        if 'detalle_factura' in data and data['detalle_factura'] and 'cabecera_factura' in data:
            # Calcular totales desde el detalle
            totales_detalle = self._calcular_totales_detalle(data['detalle_factura'])
            cab = data['cabecera_factura']
            
            # Obtener valores de cabecera
            subtotal_cab = cab.get('cabfact_subtotal', 0)
            iva_cab = cab.get('cabfact_iva', 0)
            total_cab = cab.get('cabfact_total', 0)
            
            # Log para depuración
            logger.debug("Totales calculados del detalle")
            logger.debug(f"Subtotal sin IVA: {totales_detalle['subtotal_sin_iva']:.2f}")
            logger.debug(f"Total IVA: {totales_detalle['total_iva']:.2f}")
            logger.debug(f"Total con IVA: {totales_detalle['total_con_iva']:.2f}")
            logger.debug("Totales de cabecera")
            logger.debug(f"Subtotal: {subtotal_cab:.2f}")
            logger.debug(f"IVA: {iva_cab:.2f}")
            logger.debug(f"Total: {total_cab:.2f}")
            
            # Validar que el total con IVA del detalle coincida con el total de cabecera
            # El descuento de cabecera se aplica al total final
            if abs(totales_detalle['total_con_iva'] - total_cab) > TOLERANCIA:
                # Verificar si la diferencia es el descuento de cabecera
                descuento_cab = cab.get('cabfact_valor_descuento', 0)
                total_con_descuento = totales_detalle['total_con_iva'] - descuento_cab
                if abs(total_con_descuento - total_cab) <= TOLERANCIA:
                    logger.debug(f"Descuento de cabecera aplicado: {descuento_cab:.2f}")
                else:
                    errores.append(
                        f'El total del detalle ({totales_detalle["total_con_iva"]:.2f}) no coincide '
                        f'con el total de cabecera ({total_cab:.2f})'
                    )
        
        # Validar que el total de formas_pago coincida con el total de cabecera
        if 'formas_pago' in data and 'cabecera_factura' in data:
            total_formas_pago = sum(fp.get('fpf_total_pagar', 0) for fp in data['formas_pago'])
            total_cabecera = self._round_to_2_decimals(data['cabecera_factura'].get('cabfact_total', 0))
            total_formas_pago_rounded = self._round_to_2_decimals(total_formas_pago)
            
            # Tolerancia de 0.05 por decimales
            if abs(total_formas_pago_rounded - total_cabecera) > TOLERANCIA:
                errores.append(
                    f'La suma de formas de pago ({total_formas_pago_rounded:.2f}) '
                    f'no coincide con el total de factura ({total_cabecera:.2f})'
                )
        
        if errores:
            raise ValidationError(errores)
    
    @post_load
    def separate_data(self, data, **kwargs):
        """
        Separa los datos en categorías para facilitar su procesamiento
        """
        logger.debug(f"Keys en data: {data.keys()}")
        logger.debug(f"config_impresora en data: {data.get('config_impresora')}")
        logger.debug(f"config_impresora type: {type(data.get('config_impresora'))}")
        
        # Calcular totales para metadata
        totales = self._calcular_totales_detalle(data.get('detalle_factura', []))
        
        result = {
            'restaurante': data.get('restaurante'),
            'config_impresora': data.get('config_impresora'),
            'cabecera': data.get('cabecera_factura'),
            'cliente': data.get('cliente'),
            'detalle': data.get('detalle_factura', []),
            'formas_pago': data.get('formas_pago', []),
            'metadata': {
                'total_items': len(data.get('detalle_factura', [])),
                'total_formas_pago': len(data.get('formas_pago', [])),
                'total_factura': data.get('cabecera_factura', {}).get('cabfact_total'),
                'fecha': data.get('cabecera_factura', {}).get('cabfact_fechacreacion'),
                'subtotal_sin_iva': totales['subtotal_sin_iva'],
                'total_iva': totales['total_iva'],
                'total_con_iva': totales['total_con_iva']
            }
        }
        logger.debug(f"=== Resultado final keys: {result.keys()} ===")
        logger.debug(f"Resultado config_impresora: {result.get('config_impresora')}")
        return result

# ============================================
# SCHEMA NOTA DE CRÉDITO
# ============================================
class NotaCreditoSchema(Schema):
    """
    Schema específico para nota de crédito
    """
    class Meta:
        unknown = EXCLUDE

    # Campos comunes con factura
    restaurante = fields.Nested(RestauranteSchema, required=False)
    config_impresora = fields.Nested(ConfigImpresoraSchema, required=True)
    cabecera_factura = fields.Nested(CabeceraFacturaSchema, required=True)
    cliente = fields.Nested(ClienteSchema, required=True)
    detalle_factura = fields.List(fields.Nested(DetalleFacturaSchema), required=True)
    formas_pago = fields.List(fields.Nested(FormaPagoSchema), required=True)
    
    # Campos específicos para nota de crédito (opcionales)
    # serial_impresora = fields.Str(required=False, allow_none=True)
    # fecha_factura_referencia = fields.Str(required=False, allow_none=True)
    
    @pre_load
    def unwrap_nota_credito(self, data, **kwargs):
        """Extrae el contenido de 'nota_credito' si existe"""       
        logger.debug(f"Tipo de data: {type(data)}")
        if isinstance(data, dict) and 'nota_credito' in data:
            nota_data = data['nota_credito']           
            logger.debug(f"Keys en nota_credito: {nota_data.keys()}")
            return nota_data
        return data
    
    def _calcular_totales_detalle(self, detalle_items):
        """Calcula los totales del detalle"""
        subtotal_sin_iva = 0.0
        total_iva = 0.0
        total_con_iva = 0.0
        
        for item in detalle_items:
            cantidad = item.get('dtfac_cantidad', 0)
            precio_unitario = item.get('dtfac_precio_unitario', 0)
            iva_por_unidad = item.get('dtfac_iva', 0)
            total_declarado = item.get('dtfac_total', 0)
            
            if precio_unitario == 0:
                continue
            
            item_total = total_declarado
            item_iva = cantidad * iva_por_unidad
            item_subtotal_sin_iva = item_total - item_iva
            
            subtotal_sin_iva += item_subtotal_sin_iva
            total_iva += item_iva
            total_con_iva += item_total
        
        return {
            'subtotal_sin_iva': round(subtotal_sin_iva, 2),
            'total_iva': round(total_iva, 2),
            'total_con_iva': round(total_con_iva, 2)
        }
    
    def _round_to_2_decimals(self, value):
        """Redondea a 2 decimales usando el método HALF_UP"""
        return float(Decimal(str(value)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))
    
    @post_load
    def separate_data(self, data, **kwargs):
        """Separa los datos en categorías para facilitar su procesamiento"""
        logger.debug(f"Keys en data: {data.keys()}")
        
        # Calcular totales para metadata
        totales = self._calcular_totales_detalle(data.get('detalle_factura', []))
        
        result = {
            'restaurante': data.get('restaurante'),
            'config_impresora': data.get('config_impresora'),
            'cabecera': data.get('cabecera_factura'),
            'cliente': data.get('cliente'),
            'detalle': data.get('detalle_factura', []),
            'formas_pago': data.get('formas_pago', []),
            # 'serial_impresora': data.get('serial_impresora'),
            # 'fecha_factura_referencia': data.get('fecha_factura_referencia'),
            'metadata': {
                'total_items': len(data.get('detalle_factura', [])),
                'total_formas_pago': len(data.get('formas_pago', [])),
                'total_nota_credito': data.get('cabecera_factura', {}).get('cabfact_total', 0),
                'fecha': data.get('cabecera_factura', {}).get('cabfact_fechacreacion'),
                'subtotal_sin_iva': totales['subtotal_sin_iva'],
                'total_iva': totales['total_iva'],
                'total_con_iva': totales['total_con_iva']
            }
        }
        logger.debug("=== Nota de crédito procesada ===")
        return result