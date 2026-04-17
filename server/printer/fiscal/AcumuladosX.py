# server/printer/fiscal/AcumuladosX.py
"""
Clase para manejar acumulados de reportes X
"""
from .Util import Util


class AcumuladosX(object):
    """Clase para almacenar acumulados de reportes X"""
    
    # Global variables
    _freeTax = 0
    _generalRate1 = 0
    _generalRate1Tax = 0
    _reducedRate2 = 0
    _reducedRate2Tax = 0
    _additionalRate3 = 0
    _additionalRate3Tax = 0

    def __init__(self, trama):
        if trama is not None:
            if len(trama) > 0:
                try:
                    # Separar por saltos de línea (0x0A)
                    _arrayParameter = trama.split(chr(0x0A))
                    
                    if len(_arrayParameter) >= 7:
                        util = Util()
                        self._freeTax = util.DoValueDouble(_arrayParameter[0])
                        self._generalRate1 = util.DoValueDouble(_arrayParameter[1])
                        self._reducedRate2 = util.DoValueDouble(_arrayParameter[2])
                        self._additionalRate3 = util.DoValueDouble(_arrayParameter[3])
                        self._generalRate1Tax = util.DoValueDouble(_arrayParameter[4])
                        self._reducedRate2Tax = util.DoValueDouble(_arrayParameter[5])
                        self._additionalRate3Tax = util.DoValueDouble(_arrayParameter[6])
                except Exception:
                    # En caso de error, mantener valores por defecto
                    pass
    
    def FreeTax(self):
        """Retorna el valor de ventas exentas"""
        return self._freeTax
    
    def GeneralRate1(self):
        """Retorna el valor de ventas con tasa general 1"""
        return self._generalRate1
    
    def GeneralRate1Tax(self):
        """Retorna el impuesto de tasa general 1"""
        return self._generalRate1Tax
    
    def ReducedRate2(self):
        """Retorna el valor de ventas con tasa reducida 2"""
        return self._reducedRate2

    def ReducedRate2Tax(self):
        """Retorna el impuesto de tasa reducida 2"""
        return self._reducedRate2Tax
    
    def AdditionalRate3(self):
        """Retorna el valor de ventas con tasa adicional 3"""
        return self._additionalRate3
    
    def AdditionalRate3Tax(self):
        """Retorna el impuesto de tasa adicional 3"""
        return self._additionalRate3Tax