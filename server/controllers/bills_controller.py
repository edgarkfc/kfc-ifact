#server/controllers/bills_controller.py
from tarfile import data_filter
from unittest import result

from server.controllers.helpers.create_invoice import cabeceraFacturas, factura_productos, factura_pagos
from datetime import datetime
from marshmallow import ValidationError
from server.controllers.helpers.polices import validar_mensaje_qr
from server.controllers.helpers.validators import (
    FacturaSchema
)
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
# En bills_controller.py
def armar_factura(datos):
    try:
        Schema = FacturaSchema()

        datos_validados = Schema.load(datos)
        
        cabecera_cliente = cabeceraFacturas(datos_validados)

        factura_lines = []
        
        detail_productos = factura_productos(datos_validados, factura_lines)
        
        pagos_factura = factura_pagos(factura_lines, datos_validados)

        factura_unificada = cabecera_cliente + detail_productos['factura']

        config_impresora = datos_validados.get('config_impresora', {}) 

        impresion_msgqr = validar_mensaje_qr(config_impresora.get('impresion_msgqr', False))

        if impresion_msgqr:  
            #datos = procesar_qr()
            factura_unificada.append("4\n") 

        factura_unificada.append("199\n") 
        resultado = {
            "cabecera_cliente": cabecera_cliente,
            "detail_productos": detail_productos,
            "pagos_factura": pagos_factura,
            "factura_unificada": factura_unificada            
        }
        return resultado
        
    except Exception as e:
        print(f"Error en armar_factura: {e}")
        import traceback
        traceback.print_exc()
        return "\n"
   



