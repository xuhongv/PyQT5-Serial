from PyQt5.QtCore import *
from PyQt5.QtGui import QTextCursor
from esp_at.AT import *
from datetime import datetime
import UI_Serial

from PyQt5.QtGui import QIntValidator
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QMessageBox

DEFAULT_BAUD_ARRAY = ('4800', '74880', '9600', '57600', '115200', '576000', '921600',)
GET_PORT_ARRAY = []


def at_callback_handler(obj):
    if obj['code'] == 1:
        if ui.bt_open_off_port.text() != '打开串口':
            QMessageBox.critical(MainWindow, '错误信息', '串口异常断开！')
            # 面板可操作
            checkoutPortStatus(True)
            ui.bt_open_off_port.setText('打开串口')
            refreshPort()
    else:
        buff = (obj['data'])
        now_time = datetime.now()  # 获取当前时间
        # new_time = now_time.strftime('[%H:%M:%S]')  # 打印需要的信息,依次是年月日,时分秒,注意字母大小写
        if ui.checkBox_show_hex.checkState():
            out_s = ''
            for i in range(0, len(buff)):
                out_s = out_s + '{:02X}'.format(buff[i]) + ' '

            if ui.checkBox_show_add_ctrl.checkState():
                ui.textBrowserShow.append(out_s)
            else:
                ui.textBrowserShow.insertPlainText(out_s)
            ui.textBrowserShow.moveCursor(QTextCursor.End)
        else:
            try:
                if ui.checkBox_show_add_ctrl.checkState():
                    ui.textBrowserShow.append(buff.decode('utf-8', 'ignore'))
                else:
                    ui.textBrowserShow.insertPlainText(buff.decode('utf-8', 'ignore'))

                ui.textBrowserShow.moveCursor(QTextCursor.End)
            except:
                # 乱码显示
                pass


def clear_un_show(mys):
    sl = list(mys)
    i = 0
    while i < len(sl):
        s = sl[i]
        try:
            s = s.encode('raw_unicode_escape').decode('utf-8')
            i += 1
        except:
            # 删掉它
            sl.remove(s)
    mys = ''.join(mys)
    return (mys)


def windows_key_press(event):
    if event == Qt.Key_F5:
        ui.textBrowserShow.clear()


def InitUI():
    ui.comboBox_baud.clear()
    # for item in DEFAULT_BAUD_ARRAY:
    ui.comboBox_baud.addItems(DEFAULT_BAUD_ARRAY)
    # 数据位
    ui.comboBox_Bit.addItem('8')
    ui.comboBox_Bit.addItem('7')
    ui.comboBox_Bit.addItem('6')
    ui.comboBox_Bit.addItem('5')

    # 停止位
    ui.comboBox_stop.addItem('1')
    ui.comboBox_stop.addItem('1.5')
    ui.comboBox_stop.addItem('2')

    # 校验位 'N', 'E', 'O', 'M', 'S'
    ui.comboBox_check.addItem('N')
    ui.comboBox_check.addItem('O')
    ui.comboBox_check.addItem('M')
    ui.comboBox_check.addItem('E')
    ui.comboBox_check.addItem('S')

    mATObj.set_dts(False)
    mATObj.set_rts(True)

    # 默认波特率 74880
    ui.comboBox_baud.setCurrentIndex(1)
    ui.textBrowserShow.setStyleSheet("font: 11pt \"Consolas\";")
    refreshPort()
    # 点击按钮，打开串口
    ui.bt_open_off_port.clicked.connect(onClickOpenOffPort)
    # 点击按钮，刷新串口
    ui.comboBox_port.popupAboutToBeShown.connect(refreshPort)
    #  rts
    ui.checkBox_rts.stateChanged.connect(OnClickRTS)
    #  dts
    ui.checkBox_dtr.stateChanged.connect(OnClickDTR)
    # 设置定时发送的按钮
    ui.checkBox_timer_send.stateChanged.connect(OnClickTimerSend)
    ui.lineEdit_ms_send.setValidator(QIntValidator(0, 99999999))
    #  Clear Log
    ui.btClearLog.clicked.connect(OnClickClearLog)
    #  send data
    ui.bt_send_data.clicked.connect(OnClickSendData)
    # 面板可操作
    checkoutPortStatus(True)


def OnClickClearLog():
    ui.textBrowserShow.clear()


# 点击发送
def OnClickTimerSend(state):
    print('OnClickTimerSend:',state)
    if state == QtCore.Qt.Unchecked:
        timer_send.stop()
    elif state == QtCore.Qt.Checked:
        times = ui.lineEdit_ms_send.text()
        try:
            times_send = int(times)
            timer_send.start(times_send)
        except:
            QMessageBox.critical(MainWindow, '错误信息', '请输入数字！')
            ui.checkBox_timer_send.setChecked(False)


# RTS流控
def OnClickRTS(state):
    if state == QtCore.Qt.Unchecked:
        mATObj.set_rts(False)
    elif state == QtCore.Qt.Checked:
        mATObj.set_rts(True)


# DTR流控
def OnClickDTR(state):
    if state == QtCore.Qt.Unchecked:
        mATObj.set_dts(False)
    elif state == QtCore.Qt.Checked:
        mATObj.set_dts(True)


# 刷新串口
def refreshPort():
    _ports = mATObj.initPort()
    # print(_ports)
    ui.comboBox_port.clear()
    GET_PORT_ARRAY.clear()
    if len(_ports) == 0:
        ui.comboBox_port.addItem('')
    else:
        for item in _ports:
            ui.comboBox_port.addItem(item)
            GET_PORT_ARRAY.append(item)


# 打开/关闭串口
def onClickOpenOffPort():
    if len(GET_PORT_ARRAY) == 0:
        QMessageBox.critical(MainWindow, '错误信息', '请选择串口')
    else:
        baud = DEFAULT_BAUD_ARRAY[ui.comboBox_baud.currentIndex()]
        port = GET_PORT_ARRAY[ui.comboBox_port.currentIndex()]
        str = ui.bt_open_off_port.text()
        bitIndex = ui.comboBox_Bit.currentText()
        if str == '关闭串口':
            if mATObj.try_off_port(port, baud):
                # 设置打开串口参数
                mATObj.set_default_parity(ui.comboBox_check.currentText())
                mATObj.set_default_stopbits(float(ui.comboBox_stop.currentText()))
                mATObj.set_default_port(port)
                mATObj.set_default_bytesize(int(bitIndex))
                mATObj.set_default_baudrate(baud)
                ui.bt_open_off_port.setText('打开串口')
                checkoutPortStatus(True)
            else:
                QMessageBox.critical(MainWindow, '错误信息', '串口被占用或已拔开，无法打开')
        if str == '打开串口':
            if mATObj.try_open_port(port, baud):
                checkoutPortStatus(False)
                ui.bt_open_off_port.setText('关闭串口')
            else:
                QMessageBox.critical(MainWindow, '错误信息', '串口被占用或已拔开，无法打开')


def checkoutPortStatus(isShow):
    ui.comboBox_baud.setEnabled(isShow)
    ui.comboBox_Bit.setEnabled(isShow)
    ui.comboBox_check.setEnabled(isShow)
    ui.comboBox_stop.setEnabled(isShow)
    ui.comboBox_port.setEnabled(isShow)


def OnClickSendData():
    if ui.bt_open_off_port.text() == '关闭串口':
        buff = ui.lineEdit_send_data.text().strip()
        if not ui.checkBox_send_hex.checkState():
            if not ui.checkBox_send_space_ctrl.checkState():
                mATObj.sendBuff(buff.encode('utf-8'))
            else:
                buff = buff + "\r\n"
                mATObj.sendBuff(buff.encode('utf-8'))
        else:
            send_list = []
            while buff != '':
                try:
                    num = int(buff[0:2], 16)
                except ValueError:
                    QMessageBox.critical(MainWindow, '警告', '请输入十六进制的数据，并以空格分开!')
                    return None
                buff = buff[2:].strip()
                send_list.append(num)
            input_s = bytes(send_list)
            mATObj.sendBuff(input_s)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    MainWindow = QMainWindow()
    ui = UI_Serial.Ui_AithinkerSerial()
    ui.setupUi(MainWindow)

    # # !!!修复DesignerQT5自定义QWidget时候，window不会设置调用setCentralWidget设置在中心
    MainWindow.setCentralWidget(ui.centralwidget)
    # # 设置电脑键盘回调
    ui.centralwidget.set_connect_key_press(windows_key_press)
    MainWindow.show()

    # 定时发送数据
    timer_send = QTimer()
    timer_send.timeout.connect(OnClickSendData)

    #  初始化AT
    mATObj = AT()
    mATObj.set_default_at_result_callBack(at_callback_handler)
    InitUI()
    refreshPort()

    sys.exit(app.exec_())
