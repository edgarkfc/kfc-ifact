# server/printer/fiscal/Util.py
"""
Utilidades para la impresora fiscal
"""
import logging

logger = logging.getLogger(__name__)


class Util:
    """Clase de utilidades para conversión de datos"""
    
    @staticmethod
    def DoValueDouble(value):
        """
        Convierte un valor string con formato especial a float.
        Los últimos 2 dígitos son los decimales, el resto son enteros.
        
        Ejemplo: "1234500" -> 12345.00
                 "1234567" -> 12345.67
        """
        try:
            if value is None:
                return 0.0
            
            # Convertir a string si no lo es
            if not isinstance(value, str):
                value = str(value)
            
            # Limpiar el string
            value = value.strip()
            if not value:
                return 0.0
            
            # Obtener la longitud del string
            listItemsCount = len(value)
            
            # Si tiene menos de 2 caracteres, no se puede separar
            if listItemsCount < 2:
                return float(value) if value else 0.0
            
            # Separar parte entera y decimal (últimos 2 dígitos)
            integer_part = value[0:-2]
            decimal_part = value[(listItemsCount - 2):]
            
            # Si no hay parte entera, usar 0
            if not integer_part:
                integer_part = '0'
            
            # Convertir a números
            integer_value = int(integer_part)
            decimal_value = float(decimal_part) / 100
            
            total_amount = integer_value + decimal_value
            
            return total_amount
            
        except Exception as e:
            logger.error(f"Error en DoValueDouble con valor '{value}': {e}")
            return 0.0
    
    @staticmethod
    def DoValueInt(value):
        """Convierte un valor a entero de manera segura"""
        try:
            if value is None:
                return 0
            
            if isinstance(value, (int, float)):
                return int(value)
            
            if isinstance(value, str):
                value = value.strip()
                if not value:
                    return 0
                
                # Si tiene el formato especial (últimos 2 dígitos decimales)
                if len(value) >= 2 and value.replace('.', '').replace('-', '').isdigit():
                    # Usar la misma lógica que DoValueDouble pero sin decimales
                    integer_part = value[0:-2] if len(value) > 2 else '0'
                    return int(integer_part) if integer_part else 0
            
            return int(float(value)) if value else 0
            
        except Exception as e:
            logger.error(f"Error en DoValueInt con valor '{value}': {e}")
            return 0