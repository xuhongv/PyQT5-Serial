import sys

from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import *


# widget.MineWidget   ESP8266.setCentralWidget(self.centralwidget)

class MineWidget(QWidget):

    # 定义一个信号变量，1个参数
    signalMineWidget = pyqtSignal(object)


    def set_connect_key_press(self, fun):
        self.signalMineWidget.connect(fun)

    # 检测键盘回车按键
    def keyPressEvent(self, event):
        self.signalMineWidget.emit(event.key())

    def mousePressEvent(self, event):
        self.signalMineWidget.emit(event.button())
