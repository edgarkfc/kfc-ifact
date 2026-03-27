from server.repositories.pivotqrs_repository import PivotQRSRepository
from datetime import datetime, timedelta
import random
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def procesar_qr():
    # Obtener todos los parámetros
    pivotqrs_repo = PivotQRSRepository()
    parametros = pivotqrs_repo.get_parametros_qr()
    
    if parametros:
        nropases = parametros.get('nropases')
        nrotarjetas = parametros.get('nrotarjetas')
        hora = parametros.get('hora')
        minutos = parametros.get('minutos')
        status = parametros.get('status')
        id_parametro = parametros.get('id')  # Obtener el ID del registro
        
        print(f"ID: {id_parametro}")
        print(f"Pases: {nropases}")
        print(f"Tarjetas: {nrotarjetas}")
        print(f"Tiempo: {hora}h {minutos}m")
        print(f"Status: {status}")
        
        # Usar los valores en tu lógica de QR
        
        return procesar_trama(parametros, id_parametro)
    else:
        print("Usando valores por defecto")
        # Valores por defecto (no hay ID porque es un registro nuevo)
        parametros = {
            'nropases': '4',
            'nrotarjetas': random.randint(300, 511),
            'hora': 1,
            'minutos': 0,
            'status': 'ACTIVO'
        }
        return procesar_trama(parametros, None)

def procesar_trama(parametros, id_parametro=None):
    """
    Procesa la trama QR basada en los parámetros obtenidos
    
    Args:
        parametros (dict): Diccionario con los parámetros
        id_parametro (int, optional): ID del registro en la base de datos
    
    Returns:
        str: Trama generada o None si hay error
    """
    pivotqrs_repo = None
    try:
        # Obtener valores de los parámetros
        nropases = parametros.get('nropases')
        nrotarjetas = parametros.get('nrotarjetas')
        hora = parametros.get('hora')
        minutos = parametros.get('minutos')
        
        # Validar que los parámetros necesarios existan
        if nropases is None or nrotarjetas is None or hora is None or minutos is None:
            logger.error("Faltan parámetros necesarios para procesar la trama")
            return None
        
        # Obtener la fecha y hora actual
        now = datetime.now()
        
        # Calcular hora resultante sumando horas y minutos
        hora_resultado = now + timedelta(hours=int(hora), minutes=int(minutos))
        
        # Obtener componentes de fecha y hora
        nudmes = now.month
        nuddia = now.day
        nudhora = hora_resultado.hour
        nudminuto = hora_resultado.minute
        
        # Convertir a binario con relleno de ceros
        var_pases = format(int(nropases), 'b').zfill(3)
        var_dia = format(nuddia, 'b').zfill(5)
        var_trama1 = var_pases + var_dia
        
        var_mes = format(nudmes, 'b').zfill(4)
        var_hora = format(nudhora, 'b').zfill(5)
        var_minutos = format(nudminuto, 'b').zfill(6)
        var_tarjeta = format(int(nrotarjetas), 'b').zfill(9)
        
        var_trama2 = var_tarjeta + var_mes + var_hora + var_minutos
        
        try:
            # Convertir de binario a decimal
            txt_facility_code = str(int(var_trama1, 2))
            txt_numero_de_tarjeta = str(int(var_trama2, 2))
            
            var_fc = int(txt_facility_code)
            var_card = int(txt_numero_de_tarjeta)
            
            # Validar rangos
            if (0 < var_fc <= 255) and (0 < var_card <= 16777215):
                # Conversión a hexadecimal con relleno
                var_fc_hex = format(var_fc, '02x')
                var_card_hex = format(var_card, '06x')
                
                var_trama_hex = var_fc_hex + var_card_hex
                
                # Conversión a decimal
                var_trama_dec = int(var_trama_hex, 16)
                txt_trama = str(var_trama_dec)
                
                # Actualizar el valor de nrotarjetas en la base de datos
                nrotarjetas_actual = int(nrotarjetas)
                nuevo_nrotarjetas = 1 if nrotarjetas_actual == 510 else nrotarjetas_actual + 1
                
                # Actualizar en la base de datos si tenemos el ID
                if id_parametro is not None:
                    try:
                        pivotqrs_repo = PivotQRSRepository()
                        
                        # Usar el método update_parametros con el ID y los campos a actualizar
                        resultado_update = pivotqrs_repo.update_parametros(
                            id_parametro,
                            nrotarjetas=nuevo_nrotarjetas
                        )
                        
                        if resultado_update:
                            logger.info(f"Campo nrotarjetas actualizado de {nrotarjetas_actual} a {nuevo_nrotarjetas} (ID: {id_parametro})")
                        else:
                            logger.warning(f"No se pudo actualizar nrotarjetas (ID: {id_parametro})")
                            
                    except Exception as e:
                        logger.error(f"Error al actualizar en base de datos: {e}")
                        # No detenemos el proceso, solo registramos el error
                else:
                    logger.warning("No se proporcionó ID para actualizar, saltando actualización en BD")
                
                # Log de la trama generada
                logger.info(f"Trama generada exitosamente: {txt_trama}")
                logger.debug(f"Detalles: FC={var_fc}, Card={var_card}, HEX={var_trama_hex}")
                
                return txt_trama
            else:
                logger.error(f"Valores fuera de rango - FC: {var_fc} (debe ser 1-255), Card: {var_card} (debe ser 1-16777215)")
                return None
                
        except (ValueError, TypeError) as e:
            logger.error(f"Error en la conversión de binario a entero: {e}")
            logger.debug(f"Var_Trama1: {var_trama1}, Var_Trama2: {var_trama2}")
            return None
            
    except Exception as e:
        logger.error(f"Error general en procesar_trama: {e}")
        import traceback
        logger.debug(traceback.format_exc())
        return None
    finally:
        # Limpiar recursos si es necesario
        if pivotqrs_repo and hasattr(pivotqrs_repo, 'close'):
            try:
                pivotqrs_repo.close()
            except:
                pass

def procesar_qr_con_empleados(empleados_activo=False):
    """
    Versión alternativa que considera si empleados está activo
    Similar a la lógica del código original
    
    Args:
        empleados_activo (bool): Indica si empleados está activo
    
    Returns:
        str: Trama generada
    """
    pivotqrs_repo = PivotQRSRepository()
    parametros = pivotqrs_repo.get_parametros_qr()
    
    if parametros:
        nropases = parametros.get('nropases')
        nrotarjetas = parametros.get('nrotarjetas')
        hora = parametros.get('hora')
        minutos = parametros.get('minutos')
        status = parametros.get('status')
        id_parametro = parametros.get('id')
        
        # Lógica similar al código original con $empleados
        if empleados_activo:
            nropases = '0'
            hora = 1
            minutos = 0
        
        print(f"ID: {id_parametro}")
        print(f"Pases: {nropases}")
        print(f"Tarjetas: {nrotarjetas}")
        print(f"Tiempo: {hora}h {minutos}m")
        print(f"Status: {status}")
        print(f"Empleados activo: {empleados_activo}")
        
        if status == 'ACTIVO':
            parametros_actualizados = {
                'nropases': nropases,
                'nrotarjetas': nrotarjetas,
                'hora': hora,
                'minutos': minutos,
                'status': status
            }
            return procesar_trama(parametros_actualizados, id_parametro)
    
    return None

