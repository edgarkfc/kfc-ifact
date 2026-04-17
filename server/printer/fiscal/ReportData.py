# server/printer/fiscal/ReportData.py
"""
Clase para procesar reportes de la impresora fiscal
"""
import datetime
from .Util import Util


class ReportData(object):
    """Clase para almacenar datos de reportes fiscales"""

    _numberOfLastZReport = 0
    _zReportDate = ""
    _zReportTime = ""
    _numberOfLastInvoice = 0
    _lastInvoiceDate = ""
    _lastInvoiceTime = ""
    _numberOfLastDebitNote = 0
    _numberOfLastCreditNote = 0
    _numberOfLastNonFiscal = 0

    _freeSalesTax = 0  # ventas
    _generalRate1Sale = 0
    _generalRate1Tax = 0
    _reducedRate2Sale = 0
    _reducedRate2Tax = 0
    _additionalRate3Sal = 0
    _additionalRate3Tax = 0

    _freeTaxDebit = 0  # Notas de Debito
    _generalRateDebit = 0
    _generalRateTaxDebit = 0
    _reducedRateDebit = 0
    _reducedRateTaxDebit = 0
    _additionalRateDebit = 0
    _additionalRateTaxDebit = 0
    
    _freeTaxDevolution = 0  # Notas de Credito
    _generalRateDevolution = 0
    _generalRateTaxDevolution = 0
    _reducedRateDevolution = 0
    _reducedRateTaxDevolution = 0
    _additionalRateDevolution = 0
    _additionalRateTaxDevolution = 0

    def __init__(self, trama):
        if trama is not None:
            if len(trama) > 100:
                try:
                    # Limpiar la trama
                    trama_limpia = str(trama)
                    if trama_limpia.startswith("b'") or trama_limpia.startswith('b"'):
                        trama_limpia = trama_limpia[2:-1]
                    
                    _arrayParameter = trama_limpia.split(chr(0x0A))
                    
                    if len(_arrayParameter) == 31:
                        self._parse_31_fields(_arrayParameter)
                    
                    if len(_arrayParameter) == 21:
                        self._parse_21_fields(_arrayParameter)
                    
                    if len(_arrayParameter) == 22:
                        self._parse_22_fields(_arrayParameter)
                    
                except Exception as e:
                    print(f"Error parsing ReportData: {e}")
    
    def _parse_31_fields(self, _arrayParameter):
        """Parsea formato de 31 campos"""
        util = Util()
        
        self._numberOfLastZReport = int(_arrayParameter[0])
        _hr = _arrayParameter[2][0:2]
        _mn = _arrayParameter[2][2:4]
        _dd = _arrayParameter[1][4:6]
        _mm = _arrayParameter[1][2:4]
        _aa = int(_arrayParameter[1][0:2]) + 2000
        self._zReportDate = f"{_dd}-{_mm}-{_aa}"
        self._zReportTime = f"{_hr}:{_mn}"

        self._numberOfLastInvoice = int(_arrayParameter[3])
        _hr = _arrayParameter[5][0:2]
        _mn = _arrayParameter[5][2:4]
        _dd = _arrayParameter[4][4:6]
        _mm = _arrayParameter[4][2:4]
        _aa = int(_arrayParameter[4][0:2]) + 2000
        self._lastInvoiceDate = f"{_dd}-{_mm}-{_aa}"
        self._lastInvoiceTime = f"{_hr}:{_mn}"

        self._numberOfLastCreditNote = int(_arrayParameter[6])
        self._numberOfLastDebitNote = int(_arrayParameter[7])
        self._numberOfLastNonFiscal = int(_arrayParameter[8])
        
        self._freeSalesTax = util.DoValueDouble(_arrayParameter[9])
        self._generalRate1Sale = util.DoValueDouble(_arrayParameter[10])
        self._generalRate1Tax = util.DoValueDouble(_arrayParameter[11])
        self._reducedRate2Sale = util.DoValueDouble(_arrayParameter[12])
        self._reducedRate2Tax = util.DoValueDouble(_arrayParameter[13])
        self._additionalRate3Sal = util.DoValueDouble(_arrayParameter[14])
        self._additionalRate3Tax = util.DoValueDouble(_arrayParameter[15])
        
        self._freeTaxDebit = util.DoValueDouble(_arrayParameter[16])
        self._generalRateDebit = util.DoValueDouble(_arrayParameter[17])
        self._generalRateTaxDebit = util.DoValueDouble(_arrayParameter[18])
        self._reducedRateDebit = util.DoValueDouble(_arrayParameter[19])
        self._reducedRateTaxDebit = util.DoValueDouble(_arrayParameter[20])
        self._additionalRateDebit = util.DoValueDouble(_arrayParameter[21])
        self._additionalRateTaxDebit = util.DoValueDouble(_arrayParameter[22])
        
        self._freeTaxDevolution = util.DoValueDouble(_arrayParameter[23])
        self._generalRateDevolution = util.DoValueDouble(_arrayParameter[24])
        self._generalRateTaxDevolution = util.DoValueDouble(_arrayParameter[25])
        self._reducedRateDevolution = util.DoValueDouble(_arrayParameter[26])
        self._reducedRateTaxDevolution = util.DoValueDouble(_arrayParameter[27])
        self._additionalRateDevolution = util.DoValueDouble(_arrayParameter[28])
        self._additionalRateTaxDevolution = util.DoValueDouble(_arrayParameter[29])

    def _parse_21_fields(self, _arrayParameter):
        """Parsea formato de 21 campos"""
        util = Util()
        
        self._numberOfLastZReport = int(_arrayParameter[0])
        _dd = _arrayParameter[1][4:6]
        _mm = _arrayParameter[1][2:4]
        _aa = int(_arrayParameter[1][0:2]) + 2000
        self._zReportDate = f"{_dd}-{_mm}-{_aa}"

        self._numberOfLastInvoice = int(_arrayParameter[2])
        _hr = _arrayParameter[4][0:2]
        _mn = _arrayParameter[4][2:4]
        _dd = _arrayParameter[3][4:6]
        _mm = _arrayParameter[3][2:4]
        _aa = int(_arrayParameter[3][0:2]) + 2000
        self._lastInvoiceDate = f"{_dd}-{_mm}-{_aa}"
        self._lastInvoiceTime = f"{_hr}:{_mn}"

        self._freeSalesTax = util.DoValueDouble(_arrayParameter[5])
        self._generalRate1Sale = util.DoValueDouble(_arrayParameter[6])
        self._generalRate1Tax = util.DoValueDouble(_arrayParameter[7])
        self._reducedRate2Sale = util.DoValueDouble(_arrayParameter[8])
        self._reducedRate2Tax = util.DoValueDouble(_arrayParameter[9])
        self._additionalRate3Sal = util.DoValueDouble(_arrayParameter[10])
        self._additionalRate3Tax = util.DoValueDouble(_arrayParameter[11])
        
        self._freeTaxDevolution = util.DoValueDouble(_arrayParameter[12])
        self._generalRateDevolution = util.DoValueDouble(_arrayParameter[13])
        self._generalRateTaxDevolution = util.DoValueDouble(_arrayParameter[14])
        self._reducedRateDevolution = util.DoValueDouble(_arrayParameter[15])
        self._reducedRateTaxDevolution = util.DoValueDouble(_arrayParameter[16])
        self._additionalRateDevolution = util.DoValueDouble(_arrayParameter[17])
        self._additionalRateTaxDevolution = util.DoValueDouble(_arrayParameter[18])
        
        self._numberOfLastCreditNote = int(_arrayParameter[19])

    def _parse_22_fields(self, _arrayParameter):
        """Parsea formato de 22 campos"""
        util = Util()
        
        self._numberOfLastZReport = int(_arrayParameter[0])
        _hr = _arrayParameter[2][0:2]
        _mn = _arrayParameter[2][2:4]
        _dd = _arrayParameter[1][4:6]
        _mm = _arrayParameter[1][2:4]
        _aa = int(_arrayParameter[1][0:2]) + 2000
        self._zReportDate = f"{_dd}-{_mm}-{_aa}"
        self._zReportTime = f"{_hr}:{_mn}"

        self._numberOfLastInvoice = int(_arrayParameter[3])
        _hr = _arrayParameter[5][0:2]
        _mn = _arrayParameter[5][2:4]
        _dd = _arrayParameter[4][0:2]
        _mm = _arrayParameter[4][2:4]
        _aa = int(_arrayParameter[4][4:6]) + 2000
        self._lastInvoiceDate = f"{_dd}-{_mm}-{_aa}"
        self._lastInvoiceTime = f"{_hr}:{_mn}"

        self._freeSalesTax = util.DoValueDouble(_arrayParameter[6])
        self._generalRate1Sale = util.DoValueDouble(_arrayParameter[7])
        self._generalRate1Tax = util.DoValueDouble(_arrayParameter[8])
        self._reducedRate2Sale = util.DoValueDouble(_arrayParameter[9])
        self._reducedRate2Tax = util.DoValueDouble(_arrayParameter[10])
        self._additionalRate3Sal = util.DoValueDouble(_arrayParameter[11])
        self._additionalRate3Tax = util.DoValueDouble(_arrayParameter[12])
        
        self._freeTaxDevolution = util.DoValueDouble(_arrayParameter[13])
        self._generalRateDevolution = util.DoValueDouble(_arrayParameter[14])
        self._generalRateTaxDevolution = util.DoValueDouble(_arrayParameter[15])
        self._reducedRateDevolution = util.DoValueDouble(_arrayParameter[16])
        self._reducedRateTaxDevolution = util.DoValueDouble(_arrayParameter[17])
        self._additionalRateDevolution = util.DoValueDouble(_arrayParameter[18])
        self._additionalRateTaxDevolution = util.DoValueDouble(_arrayParameter[19])
        
        self._numberOfLastCreditNote = int(_arrayParameter[20])

    # Getters
    def getNumberOfLastZReport(self):
        return self._numberOfLastZReport
    
    def getZReportDate(self):
        return self._zReportDate
    
    def getZReportTime(self):
        return self._zReportTime
    
    def getNumberOfLastInvoice(self):
        return self._numberOfLastInvoice
    
    def getLastInvoiceDate(self):
        return self._lastInvoiceDate
    
    def getLastInvoiceTime(self):
        return self._lastInvoiceTime
    
    def getNumberOfLastDebitNote(self):
        return self._numberOfLastDebitNote
    
    def getNumberOfLastCreditNote(self):
        return self._numberOfLastCreditNote
    
    def getNumberOfLastNonFiscal(self):
        return self._numberOfLastNonFiscal
    
    def getFreeSalesTax(self):
        return self._freeSalesTax
    
    def getGeneralRate1Sale(self):
        return self._generalRate1Sale
    
    def getGeneralRate1Tax(self):
        return self._generalRate1Tax
    
    def getReducedRate2Sale(self):
        return self._reducedRate2Sale
    
    def getReducedRate2Tax(self):
        return self._reducedRate2Tax
    
    def getAdditionalRate3Sal(self):
        return self._additionalRate3Sal
    
    def getAdditionalRate3Tax(self):
        return self._additionalRate3Tax