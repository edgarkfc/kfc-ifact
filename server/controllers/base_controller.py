# server/controllers/base_controller.py
"""
Clase base para controladores de documentos fiscales
Facturas y notas de crédito heredan de esta clase
"""
from abc import ABC, abstractmethod
from marshmallow import ValidationError
import logging
from datetime import datetime
from typing import Dict, Any, Tuple

logger = logging.getLogger(__name__)


class DocumentoBaseController(ABC):
    """
    Clase base para controladores de documentos fiscales
    """
    
    def __init__(self, schema_class):
        self.schema_class = schema_class
        self.tipo_documento = None
    
    def validar_documento(self, datos: Dict[str, Any]) -> Dict[str, Any]:
        """Valida el documento usando el schema correspondiente"""
        try:
            schema = self.schema_class()
            datos_validados = schema.load(datos)
            logger.info(f"✅ {self.tipo_documento} validada correctamente")
            return datos_validados
        except ValidationError as e:
            logger.error(f"❌ Error de validación en {self.tipo_documento}: {e.messages}")
            raise
        except Exception as e:
            logger.error(f"❌ Error inesperado en validación de {self.tipo_documento}: {str(e)}")
            raise ValidationError({"error": str(e)})
    
    @abstractmethod
    def procesar_documento(self, datos_validados: Dict[str, Any]) -> Dict[str, Any]:
        """Procesa el documento validado - Implementar en subclases"""
        pass
    
    
    def procesar_controller(self, datos: Dict[str, Any]) -> Tuple[Dict[str, Any], Exception, int]:
        """Controlador para procesamiento (validación + procesamiento)"""
        try:
            # Primero validar
            datos_validados = self.validar_documento(datos)
            # Luego procesar
            documento_procesado = self.procesar_documento(datos_validados)
            
            respuesta = {
                'success': True,
                'message': f'{self.tipo_documento} procesada exitosamente',
                'timestamp': datetime.now().isoformat(),
                'data': documento_procesado
            }
            return respuesta, None, 200
            
        except ValidationError as e:
            respuesta = {
                'success': False,
                'message': 'Error de validación',
                'errors': e.messages,
                'timestamp': datetime.now().isoformat()
            }
            return respuesta, e, 422
            
        except Exception as e:
            logger.error(f"Error inesperado en procesar_{self.tipo_documento.lower()}_controller: {str(e)}", exc_info=True)
            respuesta = {
                'success': False,
                'message': 'Error interno del servidor',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
            return respuesta, e, 500
    
    
    @abstractmethod
    def _obtener_resumen(self, datos_validados: Dict[str, Any]) -> Dict[str, Any]:
        """Obtiene un resumen del documento validado - Implementar en subclases"""
        pass

    def _obtener_config_impresora(self, datos_validados):
        """Obtiene configuración de impresora"""
        return datos_validados.get('config_impresora', {})
    
    def _procesar_cabecera_y_cliente(self, datos_validados):
        """Procesa cabecera y cliente"""
        from server.controllers.helpers.create_invoice import cabeceraFacturas
        return cabeceraFacturas(datos_validados)
    
    def _procesar_pagos(self, factura_lines, datos_validados):
        """Procesa pagos"""
        from server.controllers.helpers.create_invoice import factura_pagos
        return factura_pagos(factura_lines, datos_validados)