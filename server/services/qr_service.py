# server/services/qr_service.py
"""
Servicio de generación de códigos QR para facturación electrónica
Formato de trama: y + número_generado (ejemplo: y1578408916)
"""
import logging
import base64
from typing import Dict, Any, Optional
from io import BytesIO
from datetime import datetime

# IMPORTANTE: No importar nada que pueda causar circular import
# from server.controllers.helpers.algortimoqr import procesar_qr  # ← Esto se importará dentro del método

logger = logging.getLogger(__name__)


class QRService:
    """
    Servicio para generación y procesamiento de códigos QR
    Formato: y + trama_numerica (ejemplo: y1578408916)
    """
    
    # Constante: prefijo fijo para todas las tramas QR
    PREFIJO_QR = "y"
    
    def __init__(self):
        
        logger.info(f"✅ QRService inicializado con prefijo: '{self.PREFIJO_QR}'")
    
    def validar_impresion_qr(self, config_impresora: Dict[str, Any]) -> bool:
        """
        Valida si se debe imprimir QR según configuración del JSON
        """
        try:
            impresion_qr = config_impresora.get('impresion_qr', False)
            
            if not isinstance(impresion_qr, bool):
                logger.warning(f"impresion_qr debe ser booleano, recibido: {impresion_qr}")
                return False
            
            return impresion_qr
            
        except Exception as e:
            logger.error(f"Error validando impresión QR: {str(e)}")
            return False
    
    def validar_impresion_msgqr(self, config_impresora: Dict[str, Any]) -> bool:
        """
        Valida si se debe imprimir mensaje de QR según configuración
        """
        try:
            return config_impresora.get('impresion_msgqr', False)
        except Exception as e:
            logger.error(f"Error validando impresión msgqr: {str(e)}")
            return False
    
    def generar_trama_numerica(self, empleados_activo: bool = False) -> Optional[str]:
        """
        Genera la trama numérica usando el algoritmo personalizado
        """
        try:
            logger.info("🚀 Generando trama numérica con algoritmo personalizado...")
            
            # Importar aquí para evitar circular import
            from server.controllers.helpers.algortimoqr import procesar_qr, procesar_qr_con_empleados
            
            if empleados_activo:
                trama = procesar_qr_con_empleados(empleados_activo=True)
            else:
                trama = procesar_qr()
            
            if trama:
                logger.info(f"✅ Trama numérica generada: {trama}")
                return str(trama)
            else:
                logger.error("❌ Error al generar trama numérica")
                return None
                
        except Exception as e:
            logger.error(f"❌ Error generando trama numérica: {str(e)}")
            import traceback
            logger.debug(traceback.format_exc())
            return None
    
    def generar_trama_completa(self, empleados_activo: bool = False) -> Optional[str]:
        """
        Genera la trama QR completa con el formato requerido: y + número
        """
        try:
            trama_numerica = self.generar_trama_numerica(empleados_activo)
            
            if not trama_numerica:
                # Fallback: usar timestamp si falla el algoritmo
                trama_numerica = str(int(datetime.now().timestamp()))
                logger.warning(f"Usando timestamp como fallback: {trama_numerica}")
            
            trama_completa = f"{self.PREFIJO_QR}{trama_numerica}\n"
            logger.info(f"✅ Trama QR completa generada: {trama_completa}")
            return trama_completa
            
        except Exception as e:
            logger.error(f"❌ Error generando trama QR completa: {str(e)}")
            return None
    
    def _generar_qr_texto(self, texto: str) -> BytesIO:
        """Genera representación textual del QR para impresión térmica"""
        buffer = BytesIO()
        
        lineas = []
        lineas.append("╔" + "═" * 44 + "╗")
        lineas.append("║" + " " * 12 + "CÓDIGO QR" + " " * 21 + "║")
        lineas.append("╠" + "═" * 44 + "╣")
        lineas.append(f"║   {texto}" + " " * (42 - len(texto)) + "║")
        lineas.append("╠" + "═" * 44 + "╣")
        lineas.append("║   ESCANEAR PARA VERIFICAR   ║")
        lineas.append("╚" + "═" * 44 + "╝")
        
        qr_texto = "\n".join(lineas)
        buffer.write(qr_texto.encode('utf-8'))
        buffer.seek(0)
        
        return buffer
    
    def procesar_qr(self, datos: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Procesa y genera QR completo para factura"""
        try:
            config_impresora = datos.get('config_impresora', {})
            
            if not self.validar_impresion_qr(config_impresora):
                return {
                    'success': True,
                    'habilitado': False,
                    'message': 'QR no requerido según configuración'
                }
            
            empleados_activo = datos.get('empleados_activo', False)
            trama_completa = self.generar_trama_completa(empleados_activo)
            
            if not trama_completa:
                return {
                    'success': False,
                    'habilitado': False,
                    'message': 'Error al generar trama QR'
                }
            
            trama_numerica = trama_completa[1:]
            prefijo = trama_completa[0]
            
            resultado = {
                'success': True,
                'habilitado': True,
                'qr_texto': trama_completa,
                'qr_trama_numerica': trama_numerica,
                'qr_prefijo': prefijo,
                'imprimir_mensaje': self.validar_impresion_msgqr(config_impresora),
                'timestamp': datetime.now().isoformat()
            }
            
            logger.info(f"✅ QR procesado exitosamente: {trama_completa}")
            return resultado
            
        except Exception as e:
            logger.error(f"Error procesando QR: {str(e)}")
            return {
                'success': False,
                'habilitado': False,
                'message': f'Error: {str(e)}'
            }
    
    def formatear_qr_para_impresion(self, qr_texto: str, imprimir_mensaje: bool = True) -> str:
        """Formatea QR para impresión térmica"""
        return qr_texto