# server/services/print_message_service.py
"""
Servicio de mensajes personalizados para tickets de impresión
Activado por la llave 'impresion_msgqr' en config_impresora
Los mensajes se obtienen desde la tabla print_messages
"""
import logging
import random
from datetime import datetime
from typing import Dict, Any, List, Optional

# Importar repositorio
from server.repositories.print_messages_repository import PrintMessagesRepository

logger = logging.getLogger(__name__)


class PrintMessageService:
    """
    Servicio para gestionar mensajes personalizados en tickets de impresión
    Se activa cuando config_impresora.impresion_msgqr = true
    Los mensajes se obtienen desde la base de datos
    """
    
    def __init__(self):
        """Inicializa el servicio con el repositorio de mensajes"""
        self.repository = PrintMessagesRepository()
        self._mensajes_cache = None
        self._cache_timestamp = None
        logger.info("✅ PrintMessageService inicializado con repositorio BD")
    
    def _obtener_mensajes_desde_bd(self) -> Dict[str, List[str]]:
        """
        Obtiene mensajes desde la base de datos
        Estructura esperada en tabla print_messages:
        - code: tipo de mensaje (THANKS, PROMOTION, NOTICE, SPECIAL_INVOICE, SPECIAL_CREDIT_NOTE)
        - content: contenido del mensaje
        - order: orden de visualización
        - is_active: 1=activo, 0=inactivo
        """
        try:
            # Obtener todos los mensajes activos ordenados
            mensajes_bd = self.repository.get_all_active_ordered()
            
            if not mensajes_bd:
                logger.warning("No hay mensajes en BD, usando mensajes por defecto")
                return self._obtener_mensajes_por_defecto()
            
            # Organizar mensajes por código
            mensajes = {
                'agradecimientos': [],
                'promociones': [],
                'avisos': [],
                'mensajes_especiales': {
                    'FACTURA': [],
                    'NOTA_CREDITO': []
                }
            }
            
            for msg in mensajes_bd:
                code = msg.get('code', '').upper()
                content = msg.get('content', '')
                
                if not content:
                    continue
                
                # Clasificar por código
                if code == 'THANKS':
                    mensajes['agradecimientos'].append(content)
                elif code == 'PROMOTION':
                    mensajes['promociones'].append(content)
                elif code == 'NOTICE':
                    mensajes['avisos'].append(content)
                elif code == 'SPECIAL_INVOICE':
                    mensajes['mensajes_especiales']['FACTURA'].append(content)
                elif code == 'SPECIAL_CREDIT_NOTE':
                    mensajes['mensajes_especiales']['NOTA_CREDITO'].append(content)
            
            # Validar que haya mensajes, si no usar por defecto
            if not any(mensajes['agradecimientos']) and not any(mensajes['promociones']):
                logger.warning("BD sin mensajes completos, complementando con por defecto")
                default = self._obtener_mensajes_por_defecto()
                
                if not mensajes['agradecimientos']:
                    mensajes['agradecimientos'] = default['agradecimientos']
                if not mensajes['promociones']:
                    mensajes['promociones'] = default['promociones']
                if not mensajes['avisos']:
                    mensajes['avisos'] = default['avisos']
            
            logger.info(f"✅ Mensajes cargados desde BD: {sum(len(v) for v in mensajes['agradecimientos'])} agradecimientos, "
                       f"{len(mensajes['promociones'])} promociones, {len(mensajes['avisos'])} avisos")
            
            return mensajes
            
        except Exception as e:
            logger.error(f"Error obteniendo mensajes desde BD: {e}")
            return self._obtener_mensajes_por_defecto()
    
    def _obtener_mensajes_por_defecto(self) -> Dict[str, List[str]]:
        """Mensajes por defecto cuando no hay BD o está vacía"""
        return {
            'agradecimientos': [
                "¡GRACIAS POR SU COMPRA!",
                "¡VUELVA PRONTO!",
                "QUE TENGA UN EXCELENTE DÍA",
                "GRACIAS POR PREFERIRNOS",
                "¡HASTA PRONTO!"
            ],
            'promociones': [
                "SIGUENOS EN REDES SOCIALES",
                "ACUMULA PUNTOS CON SUS COMPRAS",
                "10% OFF EN SU PRÓXIMA COMPRA",
                "DESCARGA NUESTRA APP"
            ],
            'avisos': [
                "CONSERVE SU TICKET PARA GARANTÍA",
                "FACTURA VÁLIDA COMO COMPROBANTE FISCAL",
                "DEVOLUCIONES HASTA 30 DÍAS"
            ],
            'mensajes_especiales': {
                'FACTURA': [
                    "COMPROBANTE DE PAGO VÁLIDO",
                    "FACTURA ELECTRÓNICA"
                ],
                'NOTA_CREDITO': [
                    "NOTA DE CRÉDITO ELECTRÓNICA",
                    "DOCUMENTO DE ANULACIÓN"
                ]
            }
        }
    
    def _refrescar_cache(self):
        """Refresca el caché de mensajes"""
        self._mensajes_cache = self._obtener_mensajes_desde_bd()
        self._cache_timestamp = datetime.now()
        logger.debug("Caché de mensajes refrescado")
    
    def _get_mensajes(self) -> Dict[str, Any]:
        """Obtiene mensajes (con caché para mejorar rendimiento)"""
        # Refrescar caché cada 5 minutos
        if (self._mensajes_cache is None or 
            self._cache_timestamp is None or 
            (datetime.now() - self._cache_timestamp).seconds > 300):
            self._refrescar_cache()
        return self._mensajes_cache
    
    def validar_impresion_msgqr(self, config_impresora: Dict[str, Any]) -> bool:
        """
        Valida si se debe imprimir mensaje según configuración del JSON
        
        Args:
            config_impresora: Diccionario con configuración de impresora
                Ejemplo: {
                    "impresion_qr": true,
                    "impresion_msgqr": true,
                    "impresion_cupon": false
                }
            
        Returns:
            bool: True si debe imprimir mensaje
        """
        try:
            impresion_msgqr = config_impresora.get('impresion_msgqr', False)
            
            if not isinstance(impresion_msgqr, bool):
                logger.warning(f"impresion_msgqr debe ser booleano, recibido: {impresion_msgqr}")
                return False
            
            return impresion_msgqr
            
        except Exception as e:
            logger.error(f"Error validando impresión de mensaje: {str(e)}")
            return False
    
    def obtener_mensaje_agradecimiento(self, cliente: Optional[Dict] = None) -> str:
        """
        Obtiene mensaje de agradecimiento desde BD o por defecto
        
        Args:
            cliente: Datos del cliente (opcional, para personalización)
            
        Returns:
            str: Mensaje de agradecimiento
        """
        try:
            mensajes = self._get_mensajes()
            lista_mensajes = mensajes.get('agradecimientos', [])
            
            if not lista_mensajes:
                lista_mensajes = ["¡GRACIAS POR SU COMPRA!"]
            
            mensaje = random.choice(lista_mensajes)
            
            # Personalizar si hay cliente
            if cliente and cliente.get('cliente_nombres'):
                nombre = cliente.get('cliente_nombres', '').split()[0][:15]
                # Intentar personalizar el mensaje
                if "GRACIAS" in mensaje.upper():
                    mensaje = f"¡GRACIAS {nombre}!"
            
            return mensaje
            
        except Exception as e:
            logger.error(f"Error obteniendo mensaje agradecimiento: {e}")
            return "¡GRACIAS POR SU COMPRA!"
    
    def obtener_mensaje_promocional(self) -> str:
        """
        Obtiene mensaje promocional desde BD o por defecto
        
        Returns:
            str: Mensaje promocional
        """
        try:
            mensajes = self._get_mensajes()
            lista_mensajes = mensajes.get('promociones', [])
            
            if not lista_mensajes:
                return "SIGUENOS EN REDES SOCIALES"
            
            # Rotar según día de la semana
            dia = datetime.now().weekday()
            idx = dia % len(lista_mensajes)
            return lista_mensajes[idx]
            
        except Exception as e:
            logger.error(f"Error obteniendo promoción: {e}")
            return "SIGUENOS EN REDES SOCIALES"
    
    def obtener_mensaje_aviso(self) -> str:
        """
        Obtiene mensaje de aviso desde BD o por defecto
        
        Returns:
            str: Mensaje de aviso
        """
        try:
            mensajes = self._get_mensajes()
            lista_mensajes = mensajes.get('avisos', [])
            
            if not lista_mensajes:
                return "CONSERVE SU TICKET PARA GARANTÍA"
            
            return random.choice(lista_mensajes)
            
        except Exception as e:
            logger.error(f"Error obteniendo aviso: {e}")
            return "CONSERVE SU TICKET PARA GARANTÍA"
    
    def obtener_mensaje_especial(self, tipo_documento: str) -> str:
        """
        Obtiene mensaje especial según tipo de documento desde BD
        
        Args:
            tipo_documento: 'FACTURA' o 'NOTA_CREDITO'
            
        Returns:
            str: Mensaje especial
        """
        try:
            mensajes = self._get_mensajes()
            especiales = mensajes.get('mensajes_especiales', {})
            lista_mensajes = especiales.get(tipo_documento, [])
            
            if not lista_mensajes:
                return "DOCUMENTO VÁLIDO"
            
            return random.choice(lista_mensajes)
            
        except Exception as e:
            logger.error(f"Error obteniendo mensaje especial: {e}")
            return "DOCUMENTO VÁLIDO"
    
    def generar_mensajes(self, tipo_documento: str, cliente: Optional[Dict] = None) -> List[str]:
        """
        Genera lista de mensajes para el ticket
        
        Args:
            tipo_documento: 'FACTURA' o 'NOTA_CREDITO'
            cliente: Datos del cliente (opcional)
            
        Returns:
            List[str]: Lista de mensajes formateados
        """
        lineas = []
        
        try:
            # Separador
            lineas.append("─" * 48)
            
            # Mensaje especial por tipo de documento
            msg_especial = self.obtener_mensaje_especial(tipo_documento)
            lineas.append(f"  {msg_especial}")
            
            # Mensaje de agradecimiento
            msg_agradecimiento = self.obtener_mensaje_agradecimiento(cliente)
            lineas.append(f"  {msg_agradecimiento}")
            
            # Mensaje promocional
            msg_promocion = self.obtener_mensaje_promocional()
            lineas.append(f"  {msg_promocion}")
            
            # Mensaje de aviso
            msg_aviso = self.obtener_mensaje_aviso()
            lineas.append(f"  {msg_aviso}")
            
            # Fecha y hora
            ahora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            lineas.append(f"  {ahora}")
            
            lineas.append("─" * 48)
            
            logger.info(f"✅ Generados {len(lineas)} mensajes para {tipo_documento}")
            return lineas
            
        except Exception as e:
            logger.error(f"Error generando mensajes: {e}")
            return ["─" * 48, "¡GRACIAS POR SU COMPRA!", "─" * 48]
    
    def generar_mensaje_simple(self) -> str:
        """
        Genera un mensaje simple en una sola línea
        
        Returns:
            str: Mensaje simple
        """
        try:
            mensajes = [
                "¡GRACIAS POR SU COMPRA!",
                "¡VUELVA PRONTO!",
                "QUE TENGA BUEN DÍA"
            ]
            return random.choice(mensajes)
        except Exception:
            return "¡GRACIAS POR SU COMPRA!"
    
    def procesar_mensajes(self, datos: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Procesa y genera mensajes para el documento
        
        Args:
            datos: Datos del documento (debe incluir config_impresora, cabecera, cliente)
            
        Returns:
            Dict con mensajes generados
        """
        try:
            config_impresora = datos.get('config_impresora', {})
            
            # Verificar si debe imprimir mensajes
            if not self.validar_impresion_msgqr(config_impresora):
                logger.debug("Impresión de mensajes deshabilitada por config_impresora")
                return {
                    'success': True,
                    'habilitado': False,
                    'message': 'Mensajes no requeridos según configuración'
                }
            
            # Determinar tipo de documento
            tipo_documento = datos.get('tipo_documento', 'FACTURA')
            cliente = datos.get('cliente', {})
            
            # Generar mensajes
            mensajes = self.generar_mensajes(tipo_documento, cliente)
            mensaje_simple = self.generar_mensaje_simple()
            
            resultado = {
                'success': True,
                'habilitado': True,
                'mensajes': mensajes,
                'mensaje_simple': mensaje_simple,
                'timestamp': datetime.now().isoformat()
            }
            
            logger.info(f"✅ Mensajes generados para {tipo_documento}")
            return resultado
            
        except Exception as e:
            logger.error(f"Error procesando mensajes: {str(e)}")
            return {
                'success': False,
                'habilitado': False,
                'message': f'Error: {str(e)}'
            }
    
    def refrescar_cache(self):
        """Método público para forzar refresco de caché"""
        self._refrescar_cache()
        logger.info("Caché de mensajes refrescado manualmente")