import os
import sys

sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/' + '..'))

from PyQt5.QtCore import QObject, pyqtSignal
from Uart.UartSerial import *


class AT(QThread):
    # 定义一个信号变量，1个参数
    signalParseCMD = pyqtSignal(object)

    def __init__(self, _baudrate=115200, isHexSend=False, isCtrlSend=True, _port="/dev/ttyUSB0", _bytesize=8,
                 _stopbits="N",
                 _parity=serial.PARITY_NONE):
        super(AT, self).__init__()
        self.uartObj = UartSerial()
        self.port = _port
        self.baudrate = _baudrate
        self.bytesize = _bytesize
        self.stopbits = _stopbits
        self.parity = _parity
        self.isHexSend = isHexSend
        self.isCtrlSend = isCtrlSend
        self.uartObj.setCallBack(self.getUartData)

    def initPort(self):
        return self.uartObj.get_all_port()

    def sendBuff(self, strCmd, _port="", _baudrate=0, isCtrlSend=True):
        if _port == "":
            _port = self.port
        return self.uartObj.send_data(strCmd, self.isHexSend, _port, _baudrate)

    def try_off_port(self, _port, baud):
        return self.uartObj.port_close(_port, baud)

    def try_open_port(self, _port, baud):
        return self.uartObj.try_port_open(_port, baud)

    def is_port_busy(self, _port):
        return self.uartObj.is_port_open(_port, 9600)

    def set_rts(self, IsTrue):
        return self.uartObj.set_rts(IsTrue)

    def set_dts(self, IsTrue):
        return self.uartObj.set_dts(IsTrue)

    def get_rts(self):
        return self.uartObj.get_rts()

    def get_dts(self):
        return self.uartObj.get_dts()

    def getUartData(self, obj):
        # if obj['code'] == self.uartObj.CODE_RECIEVE:
        #     print("length:", obj['length'])
        #     print("data:", obj['data'])
        obj['des'] = '【模块-->MCU】 设置模块为 station 模式成功'
        self.signalParseCMD.emit(obj)

    # get and set
    def set_default_port(self, _port):
        self.port = _port

    def set_default_baudrate(self, _baudrate):
        self.baudrate = _baudrate

    def set_default_parity(self, _parity):
        self.parity = _parity
        self.uartObj.set_parity(_parity)

    def set_default_bytesize(self, _bytesize):
        self.bytesize = _bytesize
        self.uartObj.set_bytesize(_bytesize)

    def set_default_stopbits(self, _stopbits):
        self.stopbits = _stopbits
        self.uartObj.set_stopbits(_stopbits)

    # 设置回调函数
    def set_default_at_result_callBack(self, funtion):
        self.signalParseCMD.connect(funtion)
