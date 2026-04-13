# server/services/validacion_service.py
"""
Servicio de validación - Lógica común para validaciones
"""
import logging
from typing import Dict, Any, List
from decimal import Decimal, ROUND_HALF_UP

logger = logging.getLogger(__name__)


class ValidacionService:
    """Servicio para validaciones comunes"""
    
    @staticmethod
    def validar_totales(cabecera: Dict, detalle: List[Dict], tolerancia: float = 0.05) -> Dict[str, Any]:
        """
        Valida que los totales de cabecera coincidan con los del detalle
        
        Returns:
            Dict con 'valido' (bool) y 'diferencias' (list)
        """
        diferencias = []
        
        # Calcular totales del detalle
        total_detalle = sum(item.get('dtfac_total', 0) for item in detalle)
        iva_detalle = sum(item.get('dtfac_cantidad', 0) * item.get('dtfac_iva', 0) for item in detalle)
        subtotal_detalle = total_detalle - iva_detalle
        
        # Obtener totales de cabecera
        total_cabecera = cabecera.get('cabfact_total', 0)
        iva_cabecera = cabecera.get('cabfact_iva', 0)
        subtotal_cabecera = cabecera.get('cabfact_subtotal', 0)
        
        # Validar total
        if abs(total_detalle - total_cabecera) > tolerancia:
            diferencias.append({
                'campo': 'total',
                'detalle': total_detalle,
                'cabecera': total_cabecera,
                'diferencia': total_detalle - total_cabecera
            })
        
        # Validar IVA
        if abs(iva_detalle - iva_cabecera) > tolerancia:
            diferencias.append({
                'campo': 'iva',
                'detalle': iva_detalle,
                'cabecera': iva_cabecera,
                'diferencia': iva_detalle - iva_cabecera
            })
        
        # Validar subtotal
        if abs(subtotal_detalle - subtotal_cabecera) > tolerancia:
            diferencias.append({
                'campo': 'subtotal',
                'detalle': subtotal_detalle,
                'cabecera': subtotal_cabecera,
                'diferencia': subtotal_detalle - subtotal_cabecera
            })
        
        return {
            'valido': len(diferencias) == 0,
            'diferencias': diferencias,
            'totales_detalle': {
                'total': total_detalle,
                'iva': iva_detalle,
                'subtotal': subtotal_detalle
            },
            'totales_cabecera': {
                'total': total_cabecera,
                'iva': iva_cabecera,
                'subtotal': subtotal_cabecera
            }
        }
    
    @staticmethod
    def validar_formas_pago(formas_pago: List[Dict], total: float, tolerancia: float = 0.05) -> Dict[str, Any]:
        """
        Valida que la suma de formas de pago coincida con el total
        """
        suma_pagos = sum(pago.get('fpf_total_pagar', 0) for pago in formas_pago)
        
        return {
            'valido': abs(suma_pagos - total) <= tolerancia,
            'suma_pagos': suma_pagos,
            'total_esperado': total,
            'diferencia': suma_pagos - total
        }
    
    @staticmethod
    def validar_cliente(cliente: Dict) -> Dict[str, Any]:
        """
        Valida que los datos del cliente sean válidos
        """
        errores = []
        
        documento = cliente.get('cliente_documento', '')
        if not documento or documento.strip() == '':
            errores.append('El documento del cliente es obligatorio')
        
        nombres = cliente.get('cliente_nombres', '')
        if not nombres or nombres.strip() == '':
            errores.append('Los nombres del cliente son obligatorios')
        
        telefono = cliente.get('cliente_telefono', '')
        if not telefono or telefono.strip() == '':
            errores.append('El teléfono del cliente es obligatorio')
        
        return {
            'valido': len(errores) == 0,
            'errores': errores
        }
    
    @staticmethod
    def validar_productos(detalle: List[Dict]) -> Dict[str, Any]:
        """
        Valida que los productos tengan datos consistentes
        """
        errores = []
        productos_validos = []
        
        for idx, producto in enumerate(detalle):
            errores_producto = []
            
            cantidad = producto.get('dtfac_cantidad', 0)
            if cantidad <= 0:
                errores_producto.append('La cantidad debe ser mayor a 0')
            
            precio = producto.get('dtfac_precio_unitario', 0)
            if precio < 0:
                errores_producto.append('El precio no puede ser negativo')
            
            total = producto.get('dtfac_total', 0)
            if total < 0:
                errores_producto.append('El total no puede ser negativo')
            
            descripcion = producto.get('dtfac_descripcion', '')
            if not descripcion or descripcion.strip() == '':
                errores_producto.append('La descripción del producto es obligatoria')
            
            if errores_producto:
                errores.append({
                    'indice': idx,
                    'producto': descripcion,
                    'errores': errores_producto
                })
            else:
                productos_validos.append(idx)
        
        return {
            'valido': len(errores) == 0,
            'errores': errores,
            'productos_validos': productos_validos,
            'total_productos': len(detalle)
        }
    
    @staticmethod
    def redondear_decimal(valor: float, decimales: int = 2) -> float:
        """Redondea un valor decimal correctamente"""
        return float(Decimal(str(valor)).quantize(Decimal(f'0.{"0" * decimales}'), rounding=ROUND_HALF_UP))