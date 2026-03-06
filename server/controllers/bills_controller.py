#server/controllers/bills_controller.py
from server.controllers.helpers.create_invoice import cabeceraFacturas, factura_productos, factura_pagos
from datetime import datetime
from marshmallow import ValidationError
from server.controllers.helpers.validators import (
    FacturaSchema
)
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
def armar_factura(datos):

    try:
        Schema = FacturaSchema()
        datos_validados = Schema.load(datos)  
        cabecera_cliente = cabeceraFacturas(datos_validados)
        factura_lines = []
        detail_productos = factura_productos(datos_validados,factura_lines)
        resultado = factura_pagos(factura_lines, datos_validados)
    except Exception as e:
        logger.error(f"{str(e)} fn conversion_precio / helper")
        return "\n"
    return  resultado



