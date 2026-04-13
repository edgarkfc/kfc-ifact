# server/controllers/helpers/create_invoice.py
import logging
from typing import Dict, Any, List, Optional
from decimal import Decimal, ROUND_HALF_UP

# Usar qr_service como única fuente
from server.services.qr_service import QRService
from server.repositories.print_messages_repository import PrintMessagesRepository

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Instanciar QRService (única fuente de verdad para QR)
qr_service = QRService()


def cabeceraFacturas(cabeceraFactura: Dict[str, Any]) -> List[str]:
    """
    Genera la cabecera de la factura con formato específico con los datos del cliente
    
    Args:
        cabeceraFactura: Diccionario con los datos de la factura
        
    Returns:
        Lista con las líneas formateadas de la cabecera
    """
    try:
        cliente = cabeceraFactura.get('cliente', {})
        cabecera = cabeceraFactura.get('cabecera', {})
        
        tiene_delivery = 'delivery_id' in cabecera
        
        # Verificar si hay datos de cliente
        if cliente and cliente.get('cliente_nombres'):
            return _cabecera_con_cliente(cliente, cabecera, tiene_delivery)
        else:
            return _cabecera_sin_cliente(cabecera, tiene_delivery)
       
    except Exception as e:
        logger.error(f"{str(e)} fn cabeceraFacturas, cargar datos de la cabecera create_invoice / helper")
        return []


def _cabecera_con_cliente(cliente: Dict, cabecera_factura: Dict, tiene_delivery: bool) -> List[str]:
    """Genera cabecera con datos del cliente"""
    lineas = []
    
    if tiene_delivery:
        lineas.append(f"iS* {cliente.get('cliente_nombres', '')[:39]}\n")
        lineas.append(f"iR* {cliente.get('cliente_documento', '')}\n")
        lineas.append(f"i03Direccion: {cliente.get('cliente_direccion', '')[:39]}\n")
        lineas.append(f"i04Telefono: {cliente.get('cliente_telefono', '')}\n")
        lineas.append(f"i05Transaccion: {cabecera_factura.get('cabfact_id', '')}\n")
        lineas.append(f"i06Orden Delivery: {cabecera_factura.get('delivery_id', '')}\n")
    else:
        lineas.append(f"iS* {cliente.get('cliente_nombres', '')[:39]}\n")
        lineas.append(f"iR* {cliente.get('cliente_documento', '')}\n")
        lineas.append(f"i03Direccion: {cliente.get('cliente_direccion', '')[:39]}\n")
        lineas.append(f"i04Telefono: {cliente.get('cliente_telefono', '')}\n")
        lineas.append(f"i05Transaccion: {cabecera_factura.get('cabfact_id', '')}\n")
    
    return lineas


def _cabecera_sin_cliente(cabecera_factura: Dict, tiene_delivery: bool) -> List[str]:
    """Genera cabecera para consumidor final"""
    lineas = []
    
    if tiene_delivery:
        lineas.append("iS* CONSUMIDOR FINAL\n")
        lineas.append("iR* 9999999\n")
        lineas.append("i03Direccion: AV. PRINCIPAL\n")
        lineas.append("i04Telefono: 123456789\n")
        lineas.append(f"i05Transaccion: {cabecera_factura.get('cabfact_id', '')}\n")
        lineas.append(f"i06Orden Delivery: {cabecera_factura.get('delivery_id', '')}\n")
    else:
        lineas.append("iS* CONSUMIDOR FINAL\n")
        lineas.append("iR* 9999999\n")
        lineas.append("i03Direccion: AV. PRINCIPAL\n")
        lineas.append("i04Telefono: 123456789\n")
        lineas.append(f"i05Transaccion: {cabecera_factura.get('cabfact_id', '')}\n")
    
    return lineas


def factura_productos(datos_validados: Dict, factura: Optional[List] = None) -> Dict[str, Any]:
    """
    Procesa los productos de una factura y los formatea para el envio a la impresora fiscal.
    """
    try:
        n_credito = False
        
        if factura is None:
            factura = []
        
        productos = datos_validados.get('detalle', [])
        restaurante = datos_validados.get('restaurante', {})
        
        for producto in productos:
            try:
                dtfac_total = float(producto.get('dtfac_total', 0) or 0)
            except (ValueError, TypeError):
                dtfac_total = 0.0
            
            descripcion = str(producto.get('dtfac_descripcion', '') or '')
            
            if dtfac_total == 0.00:
                factura.append("@" + descripcion + "\n")
            else:
                producto_factura = conversion_precio(producto, n_credito, restaurante)
                if producto_factura:
                    factura.append(producto_factura)
                
                # Descuento por porcentaje
                try:
                    descuento_porcentaje = float(producto.get('dtfac_porcentaje_descuento', 0) or 0)
                    if descuento_porcentaje != 0:
                        factura.append(f"p-{int(descuento_porcentaje)}00\n")
                except (ValueError, TypeError):
                    pass
                
                # Descuento por monto
                try:
                    descuento_valor = float(producto.get('dtfac_valor_descuento', 0) or 0)
                    if descuento_valor != 0:
                        factura.append(f"q-{conversion_descuento_monto(descuento_valor)}\n")
                except (ValueError, TypeError):
                    pass
            
        return {'factura': factura, 'count': len(factura)}
        
    except Exception as e:
        logger.error(f"{str(e)} fn factura_productos")
        return {'factura': factura if factura else [], 'count': len(factura) if factura else 0, 'error': str(e)}


def conversion_precio(producto: Dict, n_credito: bool, restaurante: Dict) -> str:
    """
    Da formato a los valores recibidos del JSON para ser enviados a la impresora.
    """
    try:
        length_precio = 11
        length_cantidad = 8

        try:
            dtfac_precio_unitario = float(producto.get('dtfac_precio_unitario', 0) or 0)
        except (ValueError, TypeError):
            dtfac_precio_unitario = 0.0
            
        try:
            dtfac_cantidad_val = producto.get('dtfac_cantidad', 1) or 1
            if isinstance(dtfac_cantidad_val, str):
                dtfac_cantidad_val = float(dtfac_cantidad_val)
            dtfac_cantidad = int(dtfac_cantidad_val)
        except (ValueError, TypeError):
            dtfac_cantidad = 1
        
        precio_producto = format_decimal(dtfac_precio_unitario, 2)
        cantidad_producto = format_decimal(dtfac_cantidad, 3, remove_decimal=True)
        
        precio = precio_producto.zfill(length_precio)
        precio_t = precio.replace('.', '')
        cantidad = cantidad_producto.zfill(length_cantidad)
        
        descripcion = str(producto.get('dtfac_descripcion', '') or '')
        
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
        
        if impuesto_rest:
            if not n_credito:
                return f"!{precio_t}{cantidad}{descripcion}\n"
            else:
                return f"d1{precio_t}{cantidad}{descripcion}\n"
        else:
            if not n_credito:
                return f" {precio_t}{cantidad}{descripcion}\n"
            else:
                return f"d0{precio_t}{cantidad}{descripcion}\n"
                
    except Exception as e:
        logger.error(f"{str(e)} fn conversion_precio")
        return ""


def conversion_descuento_monto(pago: Any) -> str:
    """Formatea descuento por monto."""
    try:
        length_pago = 9
        
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
        
        precio_formateado = f"{precio_s_formato:.2f}"
        precio_pago = precio_formateado.replace('.', '')
        precio = precio_pago.zfill(length_pago)
        
        return precio
        
    except Exception as e:
        logger.error(f"Error formateando valor descuento {pago}: {e}")
        return "0" * 9


def format_decimal(valor: Any, decimales: int = 2, remove_decimal: bool = False) -> str:
    """Formatea un número decimal."""
    try:
        if isinstance(valor, str):
            valor = valor.strip()
            if valor == '' or valor.lower() == 'null':
                valor = '0'
        
        d = Decimal(str(valor))
        
        if decimales > 0:
            d = d.quantize(Decimal(f'0.{"0" * decimales}'), rounding=ROUND_HALF_UP)
            resultado = format(d, 'f')
        else:
            d = int(d.quantize(Decimal('1'), rounding=ROUND_HALF_UP))
            resultado = str(d)
            if remove_decimal:
                return resultado
        
        if remove_decimal and '.' in resultado:
            return resultado.replace('.', '')
            
        return resultado
        
    except Exception as e:
        logger.error(f"Error formateando decimal {valor}: {e}")
        if decimales > 0:
            return "0" + "." + "0" * decimales
        else:
            return "0"


def factura_pagos(factura: Optional[List], json_data: Dict) -> Dict[str, Any]:
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
        
        descuento_porcentaje = cabecera.get('cabfact_porcentaje_descuento', 0)
        descuento_valor = cabecera.get('cabfact_valor_descuento', 0)
        factura.append("3\n")

        # ============================================
        # QR - Usando QRService
        # ============================================
        if qr_service.validar_impresion_qr(config_impresora):
            trama_completa = qr_service.generar_trama_completa()
            if trama_completa:
                logger.info(f"✅ QR generado: {trama_completa}")
                factura.append(trama_completa + "\n")
            else:
                logger.warning("No se pudo generar la trama QR")
        
        # ============================================
        # MENSAJES PERSONALIZADOS (impresion_msgqr)
        # ============================================
        if config_impresora.get('impresion_msgqr', False):
            try:
                logger.info("📝 Generando mensajes personalizados...")
                
                # Obtener mensajes desde la base de datos
                repo = PrintMessagesRepository()
                mensajes = repo.get_all_active_ordered()
                
                logger.info(f"📋 Mensajes obtenidos: {len(mensajes)}")
                
                # Agregar cada mensaje a la factura
                for msg in mensajes:
                    content = msg.get('content', '')
                    if content:
                        # Formato para impresora fiscal
                        factura.append(f"i99{content}\n")
                        logger.debug(f"   Mensaje agregado: {content}")
                
                logger.info(f"✅ {len(mensajes)} mensajes agregados")
                
            except Exception as e:
                logger.error(f"Error procesando mensajes: {str(e)}")
                import traceback
                traceback.print_exc()
        
        # Procesar descuentos
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
        
        # Procesar formas de pago
        for pago in formas_pago:
            linea_pago = conversion_fpago(igtf, pago)
            if linea_pago:
                factura.append(linea_pago)
        
        return {'factura': factura}
        
    except Exception as e:
        logger.error(f"Error en factura_pagos: {e}")
        import traceback
        traceback.print_exc()
        return {'factura': factura, 'error': str(e)}


def conversion_fpago(igtf: Optional[float], pago: Dict) -> str:
    """Formatea pago para impresora."""
    try:
        length_pago = 12
        
        if igtf is not None:
            try:
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
            
            precio_formateado = f"{precio_s_formato:.2f}"
            precio_pago = precio_formateado.replace('.', '')
            precio = precio_pago.zfill(length_pago)
            
            return f"2{precio}\n"
        
        try:
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
        
        codigo_pago = pago.get('formapago', '00')
        if isinstance(codigo_pago, (int, float)):
            codigo_pago = str(int(codigo_pago)).zfill(2)
        elif isinstance(codigo_pago, str):
            codigo_pago = codigo_pago.strip().zfill(2)
        else:
            codigo_pago = '00'
        
        precio_formateado = f"{precio_s_formato:.2f}"
        precio_pago = precio_formateado.replace('.', '')
        precio = precio_pago.zfill(length_pago)
        
        return f"2{codigo_pago}{precio}\n"
        
    except Exception as e:
        logger.error(f"{str(e)} fn conversion_fpago")
        return "20000000000000\n"