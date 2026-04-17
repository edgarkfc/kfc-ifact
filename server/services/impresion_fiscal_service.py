# server/services/impresion_fiscal_service.py
"""
Servicio para comunicación con impresora fiscal
"""
import logging
from server.printer.fiscal import Tfhka, port

logger = logging.getLogger(__name__)


class ImpresoraFiscalService:
    """Servicio para operaciones con impresora fiscal"""
    
    def __init__(self, puerto="COM3"):
        self.printer = Tfhka()
        self.puerto = puerto
        self.conectado = False
    
    def conectar(self):
        """Conecta con la impresora fiscal"""
        try:
            self.printer.OpenFpctrl(self.puerto)
            self.conectado = True
            logger.info(f"✅ Impresora fiscal conectada en {self.puerto}")
            return True
        except Exception as e:
            logger.error(f"❌ Error conectando impresora fiscal: {e}")
            return False
    
    def desconectar(self):
        """Desconecta la impresora fiscal"""
        if self.conectado:
            self.printer.CloseFpctrl()
            self.conectado = False
            logger.info("✅ Impresora fiscal desconectada")
    
    def imprimir_factura(self, lineas_factura):
        """
        Envía las líneas de la factura a la impresora fiscal
        
        Args:
            lineas_factura: Lista de líneas formateadas
        """
        if not self.conectado:
            logger.error("Impresora no conectada")
            return False
        
        try:
            for linea in lineas_factura:
                resultado = self.printer.SendCmd(linea.strip())
                if not resultado:
                    logger.error(f"Error enviando línea: {linea}")
                    return False
            logger.info(f"✅ Factura enviada a impresora ({len(lineas_factura)} líneas)")
            return True
        except Exception as e:
            logger.error(f"Error imprimiendo factura: {e}")
            return False
    
    def obtener_estado(self):
        """Obtiene el estado de la impresora"""
        if not self.conectado:
            return "Impresora no conectada"
        return self.printer.ReadFpStatus()