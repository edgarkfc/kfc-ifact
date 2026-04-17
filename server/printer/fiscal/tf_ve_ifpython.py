# server/printer/fiscal/tf_ve_ifpython.py
# -*- coding: utf-8 -*-
"""
Clase para comunicación con impresora fiscal TfHKA
Protocolo serial con checksum LRC
"""

import serial
import operator
import time
import datetime
import logging
from functools import reduce  # ← IMPORTANTE: Agregar esta línea

logger = logging.getLogger(__name__)


class port:
    """Configuración del puerto serial"""
    portName = "COM3"
    baudRate = 9600
    dataBits = serial.EIGHTBITS
    stopBits = serial.STOPBITS_ONE
    parity = serial.PARITY_EVEN
    readBufferSize = 256
    writeBufferSize = 256
    readTimeOut = 1.5
    writeTimeOut = 5


class tf_ve_ifpython:
    """Clase base para comunicación con impresora fiscal"""
    
    bandera = False
    mdepura = False
    status = ''
    envio = ''
    error = ''
    Port = port()
    ser = None

    def OpenFpctrl(self, p):
        """Abre el puerto de comunicación con la impresora"""
        if not self.bandera:
            try:
                self.ser = serial.Serial(
                    port=p,
                    baudrate=self.Port.baudRate,
                    bytesize=self.Port.dataBits,
                    parity=self.Port.parity,
                    stopbits=self.Port.stopBits,
                    timeout=self.Port.readTimeOut,
                    writeTimeout=self.Port.writeTimeOut,
                    xonxoff=0,
                    rtscts=0
                )
                self.bandera = True
                logger.info(f"✅ Puerto {p} abierto correctamente")
                return True
            except Exception as e:
                self.bandera = False
                self.envio = f"Impresora no conectada o error accediendo al puerto {p}: {e}"
                logger.error(self.envio)
                return False

    def CloseFpctrl(self):
        """Cierra el puerto de comunicación"""
        if self.bandera and self.ser:
            self.ser.close()
            self.bandera = False
            logger.info("✅ Puerto cerrado correctamente")
        return self.bandera

    def _HandleCTSRTS(self):
        """Maneja las señales CTS/RTS"""
        try:
            self.ser.setRTS(True)
            lpri = 1
            while not self.ser.getCTS():
                time.sleep(lpri / 10)
                lpri += 1
                if lpri > 20:
                    self.ser.setRTS(False)
                    return False
            return True
        except serial.SerialException:
            return False

    def SendCmd(self, cmd):
        """Envía un comando a la impresora"""
        # Convertir string a bytes si es necesario
        if isinstance(cmd, str):
            cmd = cmd.encode('ascii', errors='ignore')
        
        if cmd == b"I0X" or cmd == b"I1X" or cmd == b"I1Z":
            self.trama = self._States_Report(cmd, 4)
            return self.trama
        if cmd == b"I0Z":
            self.trama = self._States_Report(cmd, 9)
            return self.trama
        else:
            try:
                self.ser.flushInput()
                self.ser.flushOutput()
                if self._HandleCTSRTS():
                    msj = self._AssembleQueryToSend(cmd)
                    self._write(msj)
                    rt = self._read(1)
                    if rt == b'\x06':
                        self.envio = "Status: 00  Error: 00"
                        rt = True
                    else:
                        self.envio = "Status: 00  Error: 89"
                        rt = False
                else:
                    self._GetStatusError(0, 128)
                    self.envio = "Error... CTS in False"
                    rt = False
                self.ser.setRTS(False)
            except serial.SerialException:
                rt = False
            return rt

    def SendCmdFile(self, f):
        """Envía múltiples comandos desde un archivo"""
        for linea in f:
            if linea != "":
                self.SendCmd(linea.strip())

    def _QueryCmd(self, cmd):
        """Envía comando de consulta"""
        if isinstance(cmd, str):
            cmd = cmd.encode('ascii', errors='ignore')
        
        try:
            self.ser.flushInput()
            self.ser.flushOutput()
            if self._HandleCTSRTS():
                msj = self._AssembleQueryToSend(cmd)
                self._write(msj)
                rt = True
            else:
                self._GetStatusError(0, 128)
                self.envio = "Error... CTS in False"
                rt = False
                self.ser.setRTS(False)
        except serial.SerialException:
            rt = False
        return rt

    def _FetchRow(self):
        """Obtiene una fila de respuesta"""
        while True:
            time.sleep(1)
            bytes = self.ser.inWaiting()
            if bytes > 1:
                msj = self._read(bytes)
                if msj and len(msj) > 2:
                    linea = msj[1:-1]
                    lrc = chr(self._Lrc(linea))
                    if lrc == msj[-1]:
                        self.ser.flushInput()
                        self.ser.flushOutput()
                        return msj
                    else:
                        break
            else:
                break
        return None

    def _FetchRow_Report(self, r):
        """Obtiene una fila de respuesta para reportes"""
        while True:
            time.sleep(r)
            bytes = self.ser.inWaiting()
            if bytes > 0:
                msj = self._read(bytes)
                if msj:
                    linea = msj
                    lrc = chr(self._Lrc(linea))
                    if lrc == msj:
                        self.ser.flushInput()
                        self.ser.flushOutput()
                        return msj
                    else:
                        return msj
            else:
                break
        return None

    def ReadFpStatus(self):
        """Lee el estado de la impresora fiscal"""
        if self._HandleCTSRTS():
            msj = b'\x05'  # ENQ en bytes
            self._write(msj)
            time.sleep(0.05)
            r = self._read(5)
            if len(r) == 5:
                if (r[1] ^ r[2] ^ 0x03) == r[4]:
                    return self._GetStatusError(r[1], r[2])
                else:
                    return self._GetStatusError(0, 144)
            else:
                return self._GetStatusError(0, 114)
        else:
            return self._GetStatusError(0, 128)

    def _write(self, msj):
        """Escribe datos al puerto serial"""
        if isinstance(msj, str):
            msj = msj.encode('ascii', errors='ignore')
        if self.mdepura:
            print(f'<<< {self._Debug(msj)}')
        self.ser.write(msj)

    def _read(self, bytes):
        """Lee datos del puerto serial"""
        msj = self.ser.read(bytes)
        if self.mdepura:
            print(f'>>> {self._Debug(msj)}')
        return msj

    def _AssembleQueryToSend(self, linea):
        """Ensambla el mensaje a enviar con LRC"""
        if isinstance(linea, str):
            linea = linea.encode('ascii', errors='ignore')
        lrc = self._Lrc(linea + b'\x03')
        previo = b'\x02' + linea + b'\x03' + bytes([lrc])
        return previo

    def _Lrc(self, linea):
        """Calcula el checksum LRC"""
        if isinstance(linea, str):
            linea = linea.encode('ascii')
        return reduce(operator.xor, linea)

    def _Debug(self, linea):
        """Debug de mensajes"""
        if linea is not None:
            if len(linea) == 0:
                return 'null'
            if len(linea) > 3:
                lrc = linea[-1]
                linea = linea[0:-1]
                adic = f' LRC({lrc})'
            else:
                adic = ''
            return str(linea) + adic
        return 'null'

    def _States(self, cmd):
        """Obtiene estados de la impresora"""
        if isinstance(cmd, str):
            cmd = cmd.encode('ascii')
        self._QueryCmd(cmd)
        while True:
            trama = self._FetchRow()
            if trama is None:
                break
            return trama

    def _States_Report(self, cmd, r):
        """Obtiene reportes de la impresora"""
        if isinstance(cmd, str):
            cmd = cmd.encode('ascii')
        self._QueryCmd(cmd)
        while True:
            trama = self._FetchRow_Report(r)
            if trama is None:
                break
            return trama

    def _GetStatusError(self, st, er):
        """Interpreta los códigos de estado y error"""
        st_aux = st
        st = st & ~0x04

        if (st & 0x6A) == 0x6A:
            self.status = 'En modo fiscal, carga completa de la memoria fiscal'
            status = "12"
        elif (st & 0x69) == 0x69:
            self.status = 'En modo fiscal, carga completa de la memoria fiscal'
            status = "11"
        elif (st & 0x68) == 0x68:
            self.status = 'En modo fiscal, carga completa de la memoria fiscal'
            status = "10"
        elif (st & 0x72) == 0x72:
            self.status = 'En modo fiscal, cercana carga completa'
            status = "9"
        elif (st & 0x71) == 0x71:
            self.status = 'En modo fiscal, cercana carga completa'
            status = "8"
        elif (st & 0x70) == 0x70:
            self.status = 'En modo fiscal, cercana carga completa'
            status = "7"
        elif (st & 0x62) == 0x62:
            self.status = 'En modo fiscal y emitiendo documentos no fiscales'
            status = "6"
        elif (st & 0x61) == 0x61:
            self.status = 'En modo fiscal y emitiendo documentos fiscales'
            status = "5"
        elif (st & 0x60) == 0x60:
            self.status = 'En modo fiscal y en espera'
            status = "4"
        elif (st & 0x42) == 0x42:
            self.status = 'En modo prueba y emitiendo documentos no fiscales'
            status = "3"
        elif (st & 0x41) == 0x41:
            self.status = 'En modo prueba y emitiendo documentos fiscales'
            status = "2"
        elif (st & 0x40) == 0x40:
            self.status = 'En modo prueba y en espera'
            status = "1"
        else:
            self.status = 'Status Desconocido'
            status = "0"

        if (st_aux & 0x04) == 0x04:
            self.error = ''
            error = "112"
        elif er == 128:
            self.error = 'CTS en falso'
            error = "128"
        elif er == 137:
            self.error = 'No hay respuesta'
            error = "137"
        elif er == 144:
            self.error = 'Error LRC'
            error = "144"
        elif er == 114:
            self.error = 'Impresora no responde o ocupada'
            error = "114"
        else:
            error = "0"
            self.error = 'Sin error'

        return f"{status}   {error}   {self.error}"


class Tfhka(tf_ve_ifpython):
    """Clase principal para operaciones con la impresora fiscal"""
    
    def __init__(self):
        self.trama = None
        self.ReportData = []
    
    def GetS1PrinterData(self):
        self.trama = self._States("S1")
        return self.trama
    
    def GetS2PrinterData(self):
        self.trama = self._States("S2")
        return self.trama
    
    def GetS3PrinterData(self):
        self.trama = self._States("S3")
        return self.trama
    
    def GetS4PrinterData(self):
        self.trama = self._States("S4")
        return self.trama
    
    def GetS5PrinterData(self):
        self.trama = self._States("S5")
        return self.trama
    
    def GetS6PrinterData(self):
        self.trama = self._States("S6")
        return self.trama
    
    def GetS7PrinterData(self):
        self.trama = self._States("S7")
        return self.trama
    
    def GetS8EPrinterData(self):
        self.trama = self._States("S8E")
        return self.trama
    
    def GetS8PPrinterData(self):
        self.trama = self._States("S8P")
        return self.trama
    
    def PrintXReport(self):
        self.trama = self._States_Report("I0X", 4)
        return self.trama
    
    def PrintZReport(self, *items):
        if len(items) > 0:
            mode = items[0]
            startParam = items[1]
            endParam = items[2]
            
            if isinstance(startParam, datetime.date) and isinstance(endParam, datetime.date):
                starString = startParam.strftime("%d%m%y")
                endString = endParam.strftime("%d%m%y")
                return self.SendCmd(f"I2{mode}{starString}{endString}")
            else:
                starString = str(startParam).zfill(6)
                endString = str(endParam).zfill(6)
                return self.SendCmd(f"I3{mode}{starString}{endString}")
        else:
            self.trama = self._States_Report("I0Z", 9)
            return self.trama