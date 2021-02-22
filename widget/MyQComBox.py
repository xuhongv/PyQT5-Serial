from PyQt5.QtWidgets import QComboBox
from PyQt5.QtCore import pyqtSignal


class MyQComBox(QComboBox):
    popupAboutToBeShown = pyqtSignal()  # 创建一个信号

    def showPopup(self):  # 重写showPopup函数
        super(MyQComBox, self).showPopup()
        self.popupAboutToBeShown.emit()  # 发送信号
