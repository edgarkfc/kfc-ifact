import logging
from typing import Dict, Any, Optional
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def cabeceraFacturas(cabeceraFactura: Dict[str, Any]) -> Dict[int, str]:
    """
    Genera la cabecera de la factura con formato específico
    
    Args:
        cabeceraFactura: Diccionario con los datos de la factura
        
    Returns:
        Diccionario con las líneas formateadas de la cabecera
    """
    try:
        factura = cabeceraFactura.get('factura', {})        
        cabecera_factura = factura.get('cabecera_factura', {})
        print(f"3. factura.get: {factura}")
        print(f"4. Tipo de factura: {type(factura)}")
        
        # Determinar si hay delivery
        tiene_delivery = 'delivery_id' in cabecera_factura
        print(f"5. Tipo de factura: {type(tiene_delivery)}")
        # Determinar si hay cliente
        #if 'cliente' in cabeceraFactura.get('factura', {}):   
           
        cliente = factura['cliente']          
        print(f"6. cliente.get: {type(cliente)}")
        print(f"7. cabecera_factura.get: {type(cabecera_factura)}")
        print(f"8. tiene_delivery.get: {type(tiene_delivery)}")
        print(f"9. tiene_delivery.get: {tiene_delivery}")
        return _cabecera_con_cliente(cliente, cabecera_factura, tiene_delivery)
        #else:
            #return _cabecera_sin_cliente(cabecera_factura, tiene_delivery)
            
    except Exception as e:
        logging.getLogger(__name__).info(f"{str(e)} fn cabeceraFacturas, cargar datos de la cabecera factura / helper")
        return {}


def _cabecera_con_cliente(cliente: Dict, cabecera_factura: Dict, tiene_delivery: bool) -> Dict[int, str]:
    """Genera cabecera cuando hay datos de cliente"""
    #print(f"i03Direccion: {cliente.get('cli_direccion', '')[:39]}\n")
    if tiene_delivery:
        return {
            -6: f"iS* {cliente.get('cli_nombres', '')[:39]}\n",
            -5: f"iR* {cliente.get('cli_documento', '')}\n",
            -4: f"i03Direccion: {cliente.get('cli_direccion', '')[:39]}\n",
            -3: f"i04Telefono: {cliente.get('cli_telefono', '')}\n",
            -2: f"i05Transaccion: {cabecera_factura.get('cfac_id', '')}\n",
            -1: f"i06Orden Delivery: {cabecera_factura.get('delivery_id', '')}\n",
        }
    else:
        return {            
            -5: f"iS* {cliente.get('cli_nombres', '')[:39]}\n",
            -4: f"iR* {cliente.get('cli_documento', '')}\n",
            -3: f"i03Direccion: {cliente.get('cli_direccion', '')[:39]}\n",
            -2: f"i04Telefono: {cliente.get('cli_telefono', '')}\n",
            -1: f"i05Transaccion: {cabecera_factura.get('cfac_id', '')}\n",
        }


def _cabecera_sin_cliente(cabecera_factura: Dict, tiene_delivery: bool) -> Dict[int, str]:
    """Genera cabecera para consumidor final"""
    if tiene_delivery:        
        return {
            -6: "iS* CONSUMIDOR FINAL\n",
            -5: "iR* 9999999\n",
            -4: "i03Direccion: AV. PRINCIPAL\n",
            -3: "i04Telefono: 123456789\n",
            -2: f"i05Transaccion: {cabecera_factura.get('cfac_id', '')}\n",
            -1: f"i06Orden Delivery: {cabecera_factura.get('delivery_id', '')}\n",
        }
    else:
        return {
            -5: "iS* CONSUMIDOR FINAL\n",
            -4: "iR* 9999999\n",
            -3: "i03Direccion: AV. PRINCIPAL\n",
            -2: "i04Telefono: 123456789\n",
            -1: f"i05Transaccion: {cabecera_factura.get('cfac_id', '')}\n",
        }