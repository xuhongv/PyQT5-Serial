import sys
from PyQt5.QtWidgets import QApplication, QWidget, QTextBrowser
from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import *
from PyQt5.Qt import QLineEdit, QTextEdit



class ShowQTextBrowser(QTextBrowser):


    # 检测键盘回车按键
    def keyPressEvent(self, event):
        print("按下：" + str(event.key()))
        # 举例
        if (event.key() == Qt.Key_F5):
            print('测试： Alt')

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            print("鼠标左键点击")
        elif event.button() == Qt.RightButton:
            print("鼠标右键点击")
        elif event.button() == Qt.MidButton:
            print("鼠标中键点击")
