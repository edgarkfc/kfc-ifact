# server/services/impresion_service.py
"""
Servicio de impresión - Formateo para impresora fiscal
"""
import logging
from typing import Dict, List, Tuple
from decimal import Decimal, ROUND_HALF_UP

logger = logging.getLogger(__name__)


class ImpresionService:
    """Servicio para formatear datos para impresora fiscal"""
    
    @staticmethod
    def formatear_cabecera_con_cliente(cliente: Dict, cabecera: Dict, tiene_delivery: bool) -> List[str]:
        """
        Genera cabecera de factura con datos del cliente
        """
        lineas = []
        
        # Nombre del cliente
        nombre = cliente.get('cliente_nombres', '')[:39]
        lineas.append(f"iS* {nombre}\n")
        
        # Documento
        documento = cliente.get('cliente_documento', '')
        lineas.append(f"iR* {documento}\n")
        
        # Dirección
        direccion = cliente.get('cliente_direccion', '')[:39]
        lineas.append(f"i03Direccion: {direccion}\n")
        
        # Teléfono
        telefono = cliente.get('cliente_telefono', '')
        lineas.append(f"i04Telefono: {telefono}\n")
        
        # Transacción
        transaccion = cabecera.get('cabfact_id', '')
        lineas.append(f"i05Transaccion: {transaccion}\n")
        
        # Delivery si aplica
        if tiene_delivery:
            delivery_id = cabecera.get('delivery_id', '')
            lineas.append(f"i06Orden Delivery: {delivery_id}\n")
        
        return lineas
    
    @staticmethod
    def formatear_cabecera_consumidor_final(cabecera: Dict, tiene_delivery: bool) -> List[str]:
        """
        Genera cabecera para consumidor final
        """
        lineas = [
            "iS* CONSUMIDOR FINAL\n",
            "iR* 9999999\n",
            "i03Direccion: AV. PRINCIPAL\n",
            "i04Telefono: 123456789\n",
            f"i05Transaccion: {cabecera.get('cfac_id', '')}\n"
        ]
        
        if tiene_delivery:
            lineas.append(f"i06Orden Delivery: {cabecera.get('delivery_id', '')}\n")
        
        return lineas
    
    @staticmethod
    def formatear_producto(
        producto: Dict, 
        es_nota_credito: bool = False, 
        restaurante: Dict = None
    ) -> Tuple[str, Dict]:
        """
        Formatea una línea de producto para la impresora
        
        Returns:
            Tuple con (línea formateada, metadata)
        """
        try:
            # Extraer datos
            total = float(producto.get('dtfac_total', 0) or 0)
            descripcion = str(producto.get('dtfac_descripcion', '') or '')
            
            # Producto de cortesía (total 0)
            if total == 0.00:
                return f"@{descripcion}\n", {'tipo': 'cortesia', 'total': 0}
            
            # Producto normal
            precio_unitario = float(producto.get('dtfac_precio_unitario', 0) or 0)
            cantidad = ImpresionService._parse_cantidad(producto.get('dtfac_cantidad', 1))
            
            # Obtener configuración de impuestos
            impuesto_rest = False
            if restaurante and isinstance(restaurante, dict):
                impuesto_val = restaurante.get('impuesto_rest', False)
                if isinstance(impuesto_val, str):
                    impuesto_rest = impuesto_val.lower() in ['true', '1', 'yes', 'si', 'sí']
                else:
                    impuesto_rest = bool(impuesto_val)
            
            # Formatear valores
            precio_formateado = ImpresionService._formatear_precio(precio_unitario)
            cantidad_formateada = ImpresionService._formatear_cantidad(cantidad)
            
            # Determinar código según tipo
            if impuesto_rest:
                codigo = 'd1' if es_nota_credito else '!'
            else:
                codigo = 'd0' if es_nota_credito else ' '
            
            linea = f"{codigo}{precio_formateado}{cantidad_formateada}{descripcion}\n"
            
            return linea, {
                'tipo': 'producto',
                'total': total,
                'cantidad': cantidad,
                'precio_unitario': precio_unitario,
                'con_impuesto': impuesto_rest
            }
            
        except Exception as e:
            logger.error(f"Error formateando producto: {e}")
            return "\n", {'error': str(e)}
    
    @staticmethod
    def formatear_descuento_porcentaje(porcentaje: float) -> str:
        """Formatea descuento por porcentaje"""
        if not porcentaje or float(porcentaje) == 0:
            return None
        return f"p-{int(float(porcentaje))}00\n"
    
    @staticmethod
    def formatear_descuento_monto(monto: float) -> str:
        """Formatea descuento por monto"""
        if not monto or float(monto) == 0:
            return None
        
        monto_formateado = ImpresionService._formatear_monto_9_digitos(monto)
        return f"q-{monto_formateado}\n"
    
    @staticmethod
    def formatear_pago(pago: Dict, igtf: float = None) -> str:
        """Formatea una línea de pago para la impresora"""
        try:
            length_pago = 12
            
            # Obtener valor del pago
            valor = float(pago.get('fpf_total_pagar', 0) or 0)
            
            # Si hay IGTF, usar código especial
            if igtf is not None:
                valor_igtf = float(igtf or 0)
                valor_formateado = ImpresionService._formatear_valor_pago(valor_igtf, length_pago)
                return f"2{valor_formateado}\n"
            
            # Obtener código de forma de pago
            codigo = pago.get('formapago', '00')
            if isinstance(codigo, (int, float)):
                codigo = str(int(codigo)).zfill(2)
            else:
                codigo = str(codigo).strip().zfill(2)
            
            valor_formateado = ImpresionService._formatear_valor_pago(valor, length_pago)
            return f"2{codigo}{valor_formateado}\n"
            
        except Exception as e:
            logger.error(f"Error formateando pago: {e}")
            return "20000000000000\n"
    
    @staticmethod
    def formatear_qr(datos_qr: str) -> str:
        """Formatea línea de QR"""
        return f"y{datos_qr}\n"
    
    @staticmethod
    def agregar_linea_separador() -> str:
        """Agrega línea separadora"""
        return "3\n"
    
    @staticmethod
    def agregar_linea_final() -> str:
        """Agrega línea final de factura"""
        return "199\n"
    
    @staticmethod
    def formatear_linea(texto: str, longitud: int = 48) -> str:
        """Formatea una línea de texto para la impresora"""
        if len(texto) > longitud:
            texto = texto[:longitud]
        return f"{texto}\n"
    
    @staticmethod
    def formatear_precio(precio: float) -> str:
        """Formatea precio con 2 decimales"""
        return f"{precio:.2f}"
    
    @staticmethod
    def formatear_cantidad(cantidad: int) -> str:
        """Formatea cantidad como entero"""
        return str(int(cantidad))
    
    @staticmethod
    def agregar_separador_simple() -> str:
        """Agrega línea separadora simple"""
        return "----------------------------------------\n"
    
    # Métodos privados de ayuda
    @staticmethod
    def _parse_cantidad(valor) -> int:
        """Parsea la cantidad a entero"""
        try:
            if isinstance(valor, str):
                valor = float(valor) if '.' in valor else int(valor)
            return int(valor) if valor > 0 else 1
        except (ValueError, TypeError):
            return 1
    
    @staticmethod
    def _formatear_precio(precio: float) -> str:
        """Formatea precio con 11 dígitos (sin punto decimal)"""
        precio_formateado = f"{precio:.2f}"
        precio_sin_punto = precio_formateado.replace('.', '')
        return precio_sin_punto.zfill(11)
    
    @staticmethod
    def _formatear_cantidad(cantidad: int) -> str:
        """Formatea cantidad con 8 dígitos"""
        return str(cantidad).zfill(8)
    
    @staticmethod
    def _formatear_monto_9_digitos(monto: float) -> str:
        """Formatea monto con 9 dígitos (sin punto decimal)"""
        monto_formateado = f"{monto:.2f}"
        monto_sin_punto = monto_formateado.replace('.', '')
        return monto_sin_punto.zfill(9)
    
    @staticmethod
    def _formatear_valor_pago(valor: float, length: int = 12) -> str:
        """Formatea valor de pago con longitud específica"""
        valor_formateado = f"{valor:.2f}"
        valor_sin_punto = valor_formateado.replace('.', '')
        return valor_sin_punto.zfill(length)
    
    @staticmethod
    def formatear_decimal(valor, decimales: int = 2, remove_decimal: bool = False) -> str:
        """Formatea un número decimal (similar a number_format de PHP)"""
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
            return "0"
        
    def formatear_qr(self, qr_texto: str, imprimir_mensaje: bool = True) -> str:
        """
        Formatea código QR para impresión térmica - SOLO la trama
        
        Args:
            qr_texto: Texto del QR (ejemplo: "y2330043238")
            imprimir_mensaje: No se usa, se ignora (mantenido por compatibilidad)
            
        Returns:
            str: Solo la trama QR (ejemplo: "y2330043238")
        """
        # Retornar solo el texto del QR, sin formato adicional
        return qr_texto