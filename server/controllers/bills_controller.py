#server/controllers/bills_controller.py
from server.controllers.helpers.cabecera_factura import cabeceraFacturas
from datetime import datetime

def armar_factura(datos):
        
    return cabeceraFacturas(datos)


