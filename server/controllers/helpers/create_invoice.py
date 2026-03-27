import logging
from typing import Dict, Any
from decimal import Decimal, ROUND_HALF_UP

from server.controllers.helpers.polices import validar_impresion_qr, validar_mensaje_qr
from server.controllers.helpers.algortimoqr import procesar_qr

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
logger = logging.getLogger('info')

def cabeceraFacturas(cabeceraFactura: Dict[str, Any]) -> Dict[int, str]:
    """
    Genera la cabecera de la factura con formato específico con los datos del cliente
    
    Args:
        cabeceraFactura: Diccionario con los datos de la factura
        
    Returns:
        Diccionario con las líneas formateadas de la cabecera
    """
    try:
        cliente = cabeceraFactura.get('cliente', {})
        cabecera = cabeceraFactura.get('cabecera', {})
        
        tiene_delivery = 'delivery_id' in cabecera
         # Debug: Mostrar datos del cliente
        return _cabecera_con_cliente(cliente, cabecera, tiene_delivery)
       
    except Exception as e:
        logging.getLogger(__name__).info(f"{str(e)} fn cabeceraFacturas, cargar datos de la cabecera create_invoice / helper")
        return {}

def _cabecera_con_cliente(cliente: Dict, cabecera_factura: Dict, tiene_delivery: bool) -> Dict[int, str]:
    if tiene_delivery:        
        return [
            f"iS* {cliente.get('cliente_nombres', '')[:39]}\n",
            f"iR* {cliente.get('cliente_documento', '')}\n",
            f"i03Direccion: {cliente.get('cliente_direccion', '')[:39]}\n",
            f"i04Telefono: {cliente.get('cliente_telefono', '')}\n",
            f"i05Transaccion: {cabecera_factura.get('cabfact_id', '')}\n",
            f"i06Orden Delivery: {cabecera_factura.get('delivery_id', '')}\n",
        ]
    else:        
        return [            
            f"iS* {cliente.get('cliente_nombres', '')[:39]}\n",
            f"iR* {cliente.get('cliente_documento', '')}\n",
            f"i03Direccion: {cliente.get('cliente_direccion', '')[:39]}\n",
            f"i04Telefono: {cliente.get('cliente_telefono', '')}\n",
            f"i05Transaccion: {cabecera_factura.get('cabfact_id', '')}\n",
        ]
# Si no hay datos del cliente, se puede generar una cabecera para consumidor final
def _cabecera_sin_cliente(cabecera_factura: Dict, tiene_delivery: bool) -> Dict[int, str]:
    """Genera cabecera para consumidor final"""
    if tiene_delivery:        
        return [
            "iS* CONSUMIDOR FINAL\n",
            "iR* 9999999\n",
            "i03Direccion: AV. PRINCIPAL\n",
            "i04Telefono: 123456789\n",
            f"i05Transaccion: {cabecera_factura.get('cfac_id', '')}\n",
            f"i06Orden Delivery: {cabecera_factura.get('delivery_id', '')}\n",
        ]
    else:
        return [
            "iS* CONSUMIDOR FINAL\n",
            "iR* 9999999\n",
            "i03Direccion: AV. PRINCIPAL\n",
            "i04Telefono: 123456789\n",
            f"i05Transaccion: {cabecera_factura.get('cfac_id', '')}\n",
        ]


def factura_productos(datos_validados, factura):
    """
    Procesa los productos de una factura y los formatea para el envio a la impresora fiscal.
    
    Args:
        datos_validados (dict): Diccionario con los datos validados de la factura
        factura (list): Lista donde se almacenarán las líneas formateadas (debe estar inicializada)
    
    Returns:
        dict: Diccionario con 'factura' (lista formateada) y 'count' (número de líneas)
    """
    try:
        n_credito = False
        
        # Asegurar que factura sea una lista
        if factura is None:
            factura = []
        
        # Obtener los productos del detalle
        productos = datos_validados.get('detalle', [])
        
        # Obtener datos del restaurante
        restaurante = datos_validados.get('restaurante', {})
        
        for producto in productos:
            # Convertir valores de manera segura
            try:
                dtfac_total = float(producto.get('dtfac_total', 0) or 0)
            except (ValueError, TypeError):
                dtfac_total = 0.0
            
            # Obtener la descripción del producto
            descripcion = str(producto.get('dtfac_descripcion', '') or '')
            
            if dtfac_total == 0.00:               
                factura.append("@" + descripcion + "\n")
            else:
                producto_factura = conversion_precio(producto, n_credito, restaurante)
                factura.append(producto_factura)
                
                # Creación descuento en productos por %
                try:
                    descuento_porcentaje = float(producto.get('dtfac_porcentaje_descuento', 0) or 0)
                    if descuento_porcentaje != 0:
                        factura.append(f"p-{int(descuento_porcentaje)}00\n")
                except (ValueError, TypeError):
                    pass
                
                # Creación descuento en productos por monto (formato q-000001000)
                try:
                    descuento_valor = float(producto.get('dtfac_valor_descuento', 0) or 0)
                    if descuento_valor != 0:
                        factura.append(f"q-{conversion_descuento_monto(descuento_valor)}\n")
                except (ValueError, TypeError):
                    pass            
            
        return {'factura': factura, 'count': len(factura)}
        
    except Exception as e:
        logger.error(f"{str(e)} fn factura_productos, cargando productos factura / helper")
        return {'factura': factura, 'count': len(factura) if factura else 0, 'error': str(e)}


def conversion_precio(producto, n_credito, restaurante):
    """
    Da formato a los valores recibidos del JSON para ser enviados a la impresora.
    
    Args:
        producto (dict): Diccionario con los datos del producto
        n_credito (bool): Indicador de si es nota de crédito
        restaurante (dict): Datos del restaurante con campo impuesto_rest
    
    Returns:
        str: Línea formateada del producto para la impresora
    """
    try:
        # Longitudes fijas para formato
        length_precio = 11
        length_cantidad = 8

        # Convertir valores de manera segura
        try:
            dtfac_precio_unitario = float(producto.get('dtfac_precio_unitario', 0) or 0)
        except (ValueError, TypeError):
            dtfac_precio_unitario = 0.0
            
        try:
            dtfac_cantidad_val = producto.get('dtfac_cantidad', 1) or 1
            # Asegurar que sea número
            if isinstance(dtfac_cantidad_val, str):
                dtfac_cantidad_val = float(dtfac_cantidad_val)
            dtfac_cantidad = int(dtfac_cantidad_val)
        except (ValueError, TypeError):
            dtfac_cantidad = 1
        
        # Calcular precio unitario: total / cantidad
        # if dtfac_cantidad > 0:
        #     precio_unitario = dtfac_precio_unitario
        # else:
        #     precio_unitario = 0
            
        # Formatear precio unitario con 2 decimales
        precio_producto = format_decimal(dtfac_precio_unitario, 2)
        
        # Formatear cantidad con 3 decimales sin separador de miles
        cantidad_producto = format_decimal(dtfac_cantidad, 3, remove_decimal=True)
        
        # Aplicar longitud fija con ceros a la izquierda
        precio = precio_producto.zfill(length_precio)
        
        # Eliminar el punto decimal
        precio_t = precio.replace('.', '')
        
        # Aplicar longitud fija a la cantidad
        cantidad = cantidad_producto.zfill(length_cantidad)
        
        # Obtener descripción del producto
        descripcion = str(producto.get('dtfac_descripcion', '') or '')
        
        # Obtener el valor de impuesto_rest del restaurante
        impuesto_rest = False
        if restaurante and isinstance(restaurante, dict):
            try:
                impuesto_val = restaurante.get('impuesto_rest', False)
                if isinstance(impuesto_val, str):
                    impuesto_rest = impuesto_val.lower() in ['true', '1', 'yes', 'si', 'sí']
                else:
                    impuesto_rest = bool(impuesto_val)
            except (ValueError, TypeError):
                impuesto_rest = False
        
        # Determinar el formato según impuesto_rest
        if impuesto_rest:
            # Con impuesto
            if not n_credito:
                # Factura normal con tasa 1 (!)
                return f"!{precio_t}{cantidad}{descripcion}\n"
            else:
                # Nota de crédito con tasa 1 (d1)
                return f"d1{precio_t}{cantidad}{descripcion}\n"
        else:
            # Sin impuesto (exento)
            if not n_credito:
                # Factura normal con exento (espacio)
                return f" {precio_t}{cantidad}{descripcion}\n"
            else:
                # Nota de crédito con exento (d0)
                return f"d0{precio_t}{cantidad}{descripcion}\n"
                
    except Exception as e:
        logger.error(f"{str(e)} fn conversion_precio / helper")
        return "\n"


def conversion_descuento_monto(pago):
    """
    Da formato a los valores para registrar descuento por monto.
    Formato: q-000001000
    
    Args:
        pago (float/str/int): Valor del descuento a formatear
    
    Returns:
        str: Valor formateado con 9 dígitos (sin puntos)
    """
    try:
        length_pago = 9
        
        # Convertir a float de manera segura
        try:
            if isinstance(pago, str):
                pago = pago.strip()
                if pago == '' or pago.lower() == 'null':
                    precio_s_formato = 0.0
                else:
                    precio_s_formato = float(pago)
            else:
                precio_s_formato = float(pago or 0)
        except (ValueError, TypeError):
            precio_s_formato = 0.0
        
        # Formatear con 2 decimales y eliminar punto
        precio_formateado = f"{precio_s_formato:.2f}"
        
        # Eliminar punto decimal
        precio_pago = precio_formateado.replace('.', '')
        
        # Rellenar con ceros a la izquierda hasta length_pago
        precio = precio_pago.zfill(length_pago)
        
        return precio
        
    except Exception as e:
        logger.error(f"Error formateando valor descuento {pago}: {e}")
        return "0" * 9


def format_decimal(valor, decimales=2, remove_decimal=False):
    """
    Formatea un número decimal con la cantidad especificada de decimales.
    Similar a number_format() de PHP.
    
    Args:
        valor (float/int/str): Valor a formatear
        decimales (int): Número de decimales
        remove_decimal (bool): Si es True, elimina el punto decimal
    
    Returns:
        str: Valor formateado como string
    """
    try:
        # Convertir a Decimal para mayor precisión
        if isinstance(valor, str):
            valor = valor.strip()
            if valor == '' or valor.lower() == 'null':
                valor = '0'
        
        d = Decimal(str(valor))
        
        # Redondear a la cantidad de decimales especificada
        if decimales > 0:
            d = d.quantize(Decimal(f'0.{"0" * decimales}'), rounding=ROUND_HALF_UP)
            resultado = format(d, 'f')
        else:
            d = int(d.quantize(Decimal('1'), rounding=ROUND_HALF_UP))
            resultado = str(d)
            
            if remove_decimal:
                return resultado
        
        # Eliminar el punto decimal si se solicita
        if remove_decimal and '.' in resultado:
            return resultado.replace('.', '')
            
        return resultado
        
    except Exception as e:
        logger.error(f"Error formateando decimal {valor}: {e}")
        if decimales > 0:
            return "0" + "." + "0" * decimales
        else:
            return "0"

def factura_pagos(factura, json_data):
    """
    Procesa las formas de pago de una factura y las agrega a la lista de factura.
    """
    try:
        if factura is None:
            factura = []
        
        cabecera = json_data.get('cabecera', {})
        formas_pago = json_data.get('formas_pago', [])
        config_impresora = json_data.get('config_impresora', {})  
        
        igtf = None
        
        # Descuentos
        descuento_porcentaje = cabecera.get('cabfact_porcentaje_descuento', 0)
        descuento_valor = cabecera.get('cabfact_valor_descuento', 0)
        factura.append("3\n")

        # Llamar a validar_impresion_qr
        try:
            impresion_qr = config_impresora.get('impresion_qr', False)
        except Exception as e:
            logger.error(f"Error obteniendo impresion_qr: {e}")
            impresion_qr = False

        impresionQR = validar_impresion_qr(impresion_qr)

        if impresionQR:            
            datos = procesar_qr()
            factura.append("y" + datos + "\n") 
        
        try:
            if descuento_porcentaje and float(descuento_porcentaje) != 0:
                factura.append(f"p-{int(float(descuento_porcentaje))}00\n")
        except (ValueError, TypeError):
            pass
        
        try:
            if descuento_valor and float(descuento_valor) != 0:
                factura.append(f"q-{conversion_descuento_monto(descuento_valor)}\n")
        except (ValueError, TypeError):
            pass
        
        for pago in formas_pago:
            linea_pago = conversion_fpago(igtf, pago)
            factura.append(linea_pago)
        
        return {'factura': factura}
        
    except Exception as e:
        print(f"Error en factura_pagos: {e}")
        import traceback
        traceback.print_exc()
        return {'factura': factura, 'error': str(e)}


def conversion_fpago(igtf, pago):
    """
    Da formato a los valores de pago para ser enviados a la impresora.
    
    Args:
        igtf (float/None): Valor de IGTF si aplica
        pago (dict): Diccionario con los datos de la forma de pago
    
    Returns:
        str: Línea formateada del pago para la impresora
    """
    try:
        length_pago = 12
        
        # Si hay IGTF, procesar con código "01"
        if igtf is not None:
            try:
                # Convertir IGTF a float
                if isinstance(igtf, str):
                    igtf = igtf.strip()
                    if igtf == '' or igtf.lower() == 'null':
                        precio_s_formato = 0.0
                    else:
                        precio_s_formato = float(igtf)
                else:
                    precio_s_formato = float(igtf or 0)
            except (ValueError, TypeError):
                precio_s_formato = 0.0
            
            # Formatear con 2 decimales y eliminar punto
            precio_formateado = f"{precio_s_formato:.2f}"
            precio_pago = precio_formateado.replace('.', '')
            
            # Rellenar con ceros a la izquierda
            precio = precio_pago.zfill(length_pago)
            
            return f"2{precio}\n"  # Nota: en PHP era "2" + "01" + precio, ajustar según necesidad
        
        # Procesar pago normal
        try:
            # Obtener total a pagar
            fpf_total_pagar = pago.get('fpf_total_pagar', 0)
            if isinstance(fpf_total_pagar, str):
                fpf_total_pagar = fpf_total_pagar.strip()
                if fpf_total_pagar == '' or fpf_total_pagar.lower() == 'null':
                    precio_s_formato = 0.0
                else:
                    precio_s_formato = float(fpf_total_pagar)
            else:
                precio_s_formato = float(fpf_total_pagar or 0)
        except (ValueError, TypeError):
            precio_s_formato = 0.0
        
        # Obtener código de forma de pago
        # En PHP usan 'Formapago_FacturaVarchar4', en el JSON es 'formapago'
        codigo_pago = pago.get('formapago', '00')
        if isinstance(codigo_pago, (int, float)):
            codigo_pago = str(int(codigo_pago)).zfill(2)
        elif isinstance(codigo_pago, str):
            codigo_pago = codigo_pago.strip().zfill(2)
        else:
            codigo_pago = '00'
        
        # Formatear con 2 decimales y eliminar punto
        precio_formateado = f"{precio_s_formato:.2f}"
        precio_pago = precio_formateado.replace('.', '')
        
        # Rellenar con ceros a la izquierda
        precio = precio_pago.zfill(length_pago)
        
        return f"2{codigo_pago}{precio}\n"
        
    except Exception as e:
        logger.error(f"{str(e)} fn conversion_fpago / helper")
        return "20000000000000\n"  # Línea por defecto en caso de error


def conversion_descuento_monto(pago):
    """
    Da formato a los valores para registrar descuento por monto.
    Formato: q-000001000
    
    Args:
        pago (float/str/int): Valor del descuento a formatear
    
    Returns:
        str: Valor formateado con 9 dígitos (sin puntos)
    """
    try:
        length_pago = 9
        
        # Convertir a float de manera segura
        try:
            if isinstance(pago, str):
                pago = pago.strip()
                if pago == '' or pago.lower() == 'null':
                    precio_s_formato = 0.0
                else:
                    precio_s_formato = float(pago)
            else:
                precio_s_formato = float(pago or 0)
        except (ValueError, TypeError):
            precio_s_formato = 0.0
        
        # Formatear con 2 decimales y eliminar punto
        precio_formateado = f"{precio_s_formato:.2f}"
        
        # Eliminar punto decimal
        precio_pago = precio_formateado.replace('.', '')
        
        # Rellenar con ceros a la izquierda hasta length_pago
        precio = precio_pago.zfill(length_pago)
        
        return precio
        
    except Exception as e:
        logger.error(f"Error formateando valor descuento {pago}: {e}")
        return "0" * 9





