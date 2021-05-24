from PyQt5.QtCore import *
from PyQt5.QtGui import QIcon
from esp_at.AT import *
from datetime import datetime
import UI_Serial
import json
from Uart.Espressif import *
from Uart.AliYun import *
from Utils.MqttPanleEvent import *
import time
from PyQt5.QtGui import QIntValidator
from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication, QMessageBox
from widget.QMainMyWindow import QMainMyWindow

SOFTWARE_VERSION = 'V2.0.1'

DEFAULT_BAUD_ARRAY = ('4800', '74880', '9600', '57600', '115200', '576000', '921600',)
DEFAULT_AliYun_RegionId_Show = ('上海', '深圳', '杭州', '河源', '广州', '成都', '青岛', '北京', '张家口', '呼和浩特', '乌兰察布')
DEFAULT_AliYun_RegionId = (
    'cn-shanghai', 'cn-shenzhen', 'cn-hangzhou', 'cn-heyuan', 'cn-guangzhou', 'cn-chengdu', 'cn-qingdao', 'cn-beijing',
    'cn-zhangjiakou', 'cn-huhehaote', 'cn-wulanchabu')
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
        # now_time = datetime.now()  # 获取当前时间
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
    print(event)


def save_params_local(key, value):
    mSetting = QSettings("xuhongv", "Ai-Thinker")
    mSetting.setValue(key, value)


# 从配置文件加载文件
def load_from_local():
    mSetting = QSettings("xuhongv", "Ai-Thinker")
    # mSetting.clear()

    # 小窗口控制
    ui.groupBox_customs.setHidden(mSetting.value("windows_customs_status", False, bool))
    ui.groupBox_mqtt.setHidden(mSetting.value("windows_mqtt_status", True, bool))
    ui.groupBox_TCP_UDP.setHidden(mSetting.value("windows_tcp_status", True, bool))
    ui.groupBox_aliyun.setHidden(mSetting.value("windows_aliyun_tools_status", True, bool))

    # 常规控件
    inputData = [ui.ed_customs_set_1, ui.ed_customs_set_2, ui.ed_customs_set_3,
                 ui.ed_customs_set_4, ui.ed_customs_set_5, ui.ed_customs_set_6, ui.ed_customs_set_7,
                 ui.ed_customs_set_8, ui.ed_customs_set_9, ui.ed_customs_set_10, ui.ed_customs_set_11,
                 ui.ed_customs_set_12, ui.ed_customs_set_13, ui.ed_customs_set_14, ui.ed_customs_set_15,
                 ui.ed_customs_set_16, ui.ed_customs_set_17, ui.ed_customs_set_18, ui.ed_customs_set_19,
                 ui.ed_customs_set_20, ui.ed_customs_set_21]

    groupBox_customs_text = [mSetting.value("groupBox_customs_data_1", "AT"),
                             mSetting.value("groupBox_customs_data_2", "AT+GMR"),
                             mSetting.value("groupBox_customs_data_3", "AT+RST"),
                             mSetting.value("groupBox_customs_data_4", "AT+CWMODE=1"),
                             mSetting.value("groupBox_customs_data_5", "AT+CWJAP=\"aiot@xuhongv\",\"xuhong12345678\""),
                             mSetting.value("groupBox_customs_data_6", ""),
                             mSetting.value("groupBox_customs_data_7", ""),
                             mSetting.value("groupBox_customs_data_8", ""),
                             mSetting.value("groupBox_customs_data_9", ""),
                             mSetting.value("groupBox_customs_data_10", ""),
                             mSetting.value("groupBox_customs_data_11", ""),
                             mSetting.value("groupBox_customs_data_12", ""),
                             mSetting.value("groupBox_customs_data_13", ""),
                             mSetting.value("groupBox_customs_data_14", ""),
                             mSetting.value("groupBox_customs_data_15", ""),
                             mSetting.value("groupBox_customs_data_16", ""),
                             mSetting.value("groupBox_customs_data_17", ""),
                             mSetting.value("groupBox_customs_data_18", ""),
                             mSetting.value("groupBox_customs_data_19", ""),
                             mSetting.value("groupBox_customs_data_20", ""),
                             mSetting.value("groupBox_customs_data_21", "")
                             ]

    for index in range(len(groupBox_customs_text)):
        inputData[index].setText(groupBox_customs_text[index])

    # TCP UDP的参数配置
    ui.ed_tcp_udp_broker.setText(mSetting.value("ed_tcp_udp_broker", "www.xuhong.com", str))
    ui.ed_tcp_udp_port.setText(mSetting.value("ed_tcp_udp_port", '8888', str))
    ui.ed_tcp_udp_ssid.setText(mSetting.value("ed_tcp_udp_ssid", "xuhongv@iot", str))
    ui.ed_tcp_udp_password.setText(mSetting.value("ed_tcp_udp_password", "xuhong12345678", str))
    ui.ed_tcp_udp_content.setText(mSetting.value("ed_tcp_udp_content", "I am a aithinker fan", str))
    ui.cb_protocol_tcp_udp_boot.setCurrentIndex(mSetting.value("cb_protocol_tcp_udp_boot", 0))
    ui.cb_protocol_tcp_udp.setCurrentIndex(mSetting.value("cb_protocol_tcp_udp", 0))

    # MQTT参数配置
    ui.ed_broker.setText(mSetting.value("textMQTTBroker", "www.xuhong.com", str))
    ui.ed_port.setText(mSetting.value("textMQTTPort", "1883", str))
    ui.ed_username.setText(mSetting.value("textMQTTUserName", "admin", str))
    ui.ed_password.setText(mSetting.value("textMQTTPassword", "public", str))
    ui.ed_clientId.setText(mSetting.value("textMQTTClientId", "clientId", str))
    ui.ed_mqtt_sub_topic.setText(mSetting.value("textMQTTSubTopic", "/topic/sub", str))
    ui.ed_mqtt_pub_topic.setText(mSetting.value("textMQTTPubTopic", "/topic/pub", str))
    ui.ed_mqtt_pub_msg.setText(mSetting.value("textMQTTPubMsg", "I am a aithinker fan", str))
    ui.ed_ssid.setText(mSetting.value("textMQTTRouterSSID", "xuhongv@iot", str))
    ui.ed_SSIDpassword.setText(mSetting.value("textMQTTRouterPWD", "xuhong12345678", str))

    # 阿里云
    ui.ed_aliyun_productKey.setText(mSetting.value("ed_aliyun_productKey", "a1gusYr8Z8b", str))
    ui.ed_aliyun_device_name.setText(mSetting.value("ed_aliyun_device_name", "6nA0KPt4eri5cXuPKX8E", str))
    ui.ed_aliyun_device_secret.setText(
        mSetting.value("ed_aliyun_device_secret", "ZmcUHcDNuSfjI28jeSWkRIOClLcU3iFD", str))
    ui.ed_aliyun_mac_sn.setText(mSetting.value("ed_aliyun_mac_sn", "FC5056CAF001", str))
    ui.ed_aliyun_Region_Id.setCurrentIndex(mSetting.value("ed_aliyun_Region_Id", 0))


def InitUI():
    ui.comboBox_baud.clear()
    # for item in DEFAULT_BAUD_ARRAY:
    ui.comboBox_baud.addItems(DEFAULT_BAUD_ARRAY)
    ui.comboBox_baud.setCurrentIndex(4)
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

    # 模组选项
    ui.cb_mqtt_select_module_type.addItem('ESP系列')
    ui.cb_module_type_tcp_udp.addItem('ESP系列')

    ui.cb_protocol_tcp_udp.addItem('TCP')
    ui.cb_protocol_tcp_udp.addItem('UDP')
    ui.cb_protocol_tcp_udp_boot.addItem('上电后透传')
    ui.cb_protocol_tcp_udp_boot.addItem('上电后不透传')
    ui.ed_aliyun_Region_Id.clear()
    ui.ed_aliyun_Region_Id.addItems(DEFAULT_AliYun_RegionId_Show)

    mATObj.set_dts(False)
    mATObj.set_rts(False)
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
    # 隐藏拓展面板
    ui.bt_open_off_expand_customs.clicked.connect(OnClickOffCustomsExpand)
    ui.bt_open_off_expand_mqtt.clicked.connect(OnClickOffMQTTExpand)
    ui.bt_open_off_expand_tcp_udp.clicked.connect(OnClickOffTcpUdpExpand)
    ui.bt_open_off_expand_aliyun.clicked.connect(OnClickOffAliyunExpand)

    # 运行模式
    ui.bt_checkout_run.clicked.connect(OnClickCheckOutRun)
    # 示例创建
    initMqttUI()
    initCustomsUI()
    initTCP_UDP_UI()
    init_AliYun_UI()


def OnClickCheckOutRun():
    mATObj.set_rts(True)
    mATObj.set_dts(False)
    time.sleep(0.1)
    mATObj.set_dts(True)
    ui.checkBox_rts.setChecked(True)
    ui.checkBox_dtr.setChecked(True)


def OnClickOffMQTTExpand():
    ui.groupBox_mqtt.setHidden(not ui.groupBox_mqtt.isHidden())
    save_params_local("windows_mqtt_status", ui.groupBox_mqtt.isHidden())


def OnClickOffCustomsExpand():
    ui.groupBox_customs.setHidden(not ui.groupBox_customs.isHidden())
    save_params_local("windows_customs_status", ui.groupBox_customs.isHidden())


def OnClickOffTcpUdpExpand():
    ui.groupBox_TCP_UDP.setHidden(not ui.groupBox_TCP_UDP.isHidden())
    save_params_local("windows_tcp_status", ui.groupBox_TCP_UDP.isHidden())


def OnClickOffAliyunExpand():
    ui.groupBox_aliyun.setHidden(not ui.groupBox_aliyun.isHidden())
    save_params_local("windows_aliyun_tools_status", ui.groupBox_aliyun.isHidden())


def OnClickClearLog():
    ui.textBrowserShow.clear()


# 点击发送
def OnClickTimerSend(state):
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
    if ui.checkBox_send_space_ctrl.checkState() == 0:
        SendDataFuntion(True)
    else:
        SendDataFuntion(False)


def SendDataFuntion(isNotNewLine=False):
    ui.checkBox_send_space_ctrl.setChecked(not isNotNewLine)
    if ui.bt_open_off_port.text() == '关闭串口':
        buff = ui.lineEdit_send_data.text().strip()
        if not ui.checkBox_send_hex.checkState():
            if isNotNewLine:
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


#  customs AT指令窗口 ------------------------------------------------------ STRAT  -------------------------------------
def initCustomsUI():
    ui.bt_customs_send_1.clicked.connect(OnclickCustoms1)
    ui.bt_customs_send_2.clicked.connect(OnclickCustoms2)
    ui.bt_customs_send_3.clicked.connect(OnclickCustoms3)
    ui.bt_customs_send_4.clicked.connect(OnclickCustoms4)
    ui.bt_customs_send_5.clicked.connect(OnclickCustoms5)
    ui.bt_customs_send_6.clicked.connect(OnclickCustoms6)
    ui.bt_customs_send_7.clicked.connect(OnclickCustoms7)
    ui.bt_customs_send_8.clicked.connect(OnclickCustoms8)
    ui.bt_customs_send_9.clicked.connect(OnclickCustoms9)
    ui.bt_customs_send_10.clicked.connect(OnclickCustoms10)
    ui.bt_customs_send_11.clicked.connect(OnclickCustoms11)
    ui.bt_customs_send_12.clicked.connect(OnclickCustoms12)
    ui.bt_customs_send_13.clicked.connect(OnclickCustoms13)
    ui.bt_customs_send_14.clicked.connect(OnclickCustoms14)
    ui.bt_customs_send_15.clicked.connect(OnclickCustoms15)
    ui.bt_customs_send_16.clicked.connect(OnclickCustoms16)
    ui.bt_customs_send_17.clicked.connect(OnclickCustoms17)
    ui.bt_customs_send_18.clicked.connect(OnclickCustoms18)
    ui.bt_customs_send_19.clicked.connect(OnclickCustoms19)
    ui.bt_customs_send_20.clicked.connect(OnclickCustoms20)
    ui.bt_customs_send_21.clicked.connect(OnclickCustoms21)


def OnclickCustoms1():
    ui.lineEdit_send_data.setText(ui.ed_customs_set_1.text())
    save_params_local('groupBox_customs_data_1', ui.ed_customs_set_1.text())
    SendDataFuntion()


def OnclickCustoms2():
    ui.lineEdit_send_data.setText(ui.ed_customs_set_2.text())
    save_params_local('groupBox_customs_data_2', ui.ed_customs_set_2.text())
    SendDataFuntion()


def OnclickCustoms3():
    ui.lineEdit_send_data.setText(ui.ed_customs_set_3.text())
    save_params_local('groupBox_customs_data_3', ui.ed_customs_set_3.text())
    SendDataFuntion()


def OnclickCustoms4():
    ui.lineEdit_send_data.setText(ui.ed_customs_set_4.text())
    save_params_local('groupBox_customs_data_4', ui.ed_customs_set_4.text())
    SendDataFuntion()


def OnclickCustoms5():
    ui.lineEdit_send_data.setText(ui.ed_customs_set_5.text())
    save_params_local('groupBox_customs_data_5', ui.ed_customs_set_5.text())
    SendDataFuntion()


def OnclickCustoms6():
    ui.lineEdit_send_data.setText(ui.ed_customs_set_6.text())
    save_params_local('groupBox_customs_data_6', ui.ed_customs_set_6.text())
    SendDataFuntion()


def OnclickCustoms7():
    ui.lineEdit_send_data.setText(ui.ed_customs_set_7.text())
    save_params_local('groupBox_customs_data_7', ui.ed_customs_set_7.text())
    SendDataFuntion()


def OnclickCustoms8():
    ui.lineEdit_send_data.setText(ui.ed_customs_set_8.text())
    save_params_local('groupBox_customs_data_8', ui.ed_customs_set_8.text())
    SendDataFuntion()


def OnclickCustoms9():
    ui.lineEdit_send_data.setText(ui.ed_customs_set_9.text())
    save_params_local('groupBox_customs_data_9', ui.ed_customs_set_9.text())
    SendDataFuntion()


def OnclickCustoms10():
    ui.lineEdit_send_data.setText(ui.ed_customs_set_10.text())
    save_params_local('groupBox_customs_data_10', ui.ed_customs_set_10.text())
    SendDataFuntion()


def OnclickCustoms11():
    ui.lineEdit_send_data.setText(ui.ed_customs_set_11.text())
    save_params_local('groupBox_customs_data_11', ui.ed_customs_set_11.text())
    SendDataFuntion()


def OnclickCustoms12():
    ui.lineEdit_send_data.setText(ui.ed_customs_set_12.text())
    save_params_local('groupBox_customs_data_12', ui.ed_customs_set_12.text())
    SendDataFuntion()


def OnclickCustoms13():
    ui.lineEdit_send_data.setText(ui.ed_customs_set_13.text())
    save_params_local('groupBox_customs_data_13', ui.ed_customs_set_13.text())
    SendDataFuntion()


def OnclickCustoms14():
    ui.lineEdit_send_data.setText(ui.ed_customs_set_14.text())
    save_params_local('groupBox_customs_data_14', ui.ed_customs_set_14.text())
    SendDataFuntion()


def OnclickCustoms15():
    ui.lineEdit_send_data.setText(ui.ed_customs_set_15.text())
    save_params_local('groupBox_customs_data_15', ui.ed_customs_set_15.text())
    SendDataFuntion()


def OnclickCustoms16():
    ui.lineEdit_send_data.setText(ui.ed_customs_set_16.text())
    save_params_local('groupBox_customs_data_16', ui.ed_customs_set_16.text())
    SendDataFuntion()


def OnclickCustoms17():
    ui.lineEdit_send_data.setText(ui.ed_customs_set_17.text())
    save_params_local('groupBox_customs_data_17', ui.ed_customs_set_17.text())
    SendDataFuntion()


def OnclickCustoms18():
    ui.lineEdit_send_data.setText(ui.ed_customs_set_18.text())
    save_params_local('groupBox_customs_data_18', ui.ed_customs_set_18.text())
    SendDataFuntion()


def OnclickCustoms19():
    ui.lineEdit_send_data.setText(ui.ed_customs_set_19.text())
    save_params_local('groupBox_customs_data_19', ui.ed_customs_set_19.text())
    SendDataFuntion()


def OnclickCustoms20():
    ui.lineEdit_send_data.setText(ui.ed_customs_set_20.text())
    save_params_local('groupBox_customs_data_20', ui.ed_customs_set_20.text())
    SendDataFuntion()


def OnclickCustoms21():
    ui.lineEdit_send_data.setText(ui.ed_customs_set_21.text())
    save_params_local('groupBox_customs_data_21', ui.ed_customs_set_21.text())
    SendDataFuntion()


#  TCP UDP AT指令窗口 ------------------------------------------------------ STRAT  -------------------------------------
def init_AliYun_UI():
    ui.bt_aliyun_create.clicked.connect(OnclickAliyunCreate)


def OnclickAliyunCreate():
    textAliyunProductKey = ui.ed_aliyun_productKey.text()
    textAliyunDevice_name = ui.ed_aliyun_device_name.text()
    textAliyunDeviceSecret = ui.ed_aliyun_device_secret.text()
    textAliyunMacSn = ui.ed_aliyun_mac_sn.text()
    textRegionId = ui.ed_aliyun_Region_Id.currentIndex()

    inputData = [ui.ed_aliyun_broker, ui.ed_aliyun_port, ui.ed_aliyun_username, ui.ed_aliyun_password,
                 ui.ed_aliyun_clientId,
                 ui.ed_aliyun_sub_topic, ui.ed_aliyun_pub_topic]

    data = mAliYunMQTT.getAliYunMQTT(DEFAULT_AliYun_RegionId[textRegionId], textAliyunMacSn, textAliyunProductKey,
                                     textAliyunDevice_name, textAliyunDeviceSecret)

    for index in range(len(data['content'])):
        inputData[index].setText(data['content'][index])

    save_params_local('ed_aliyun_productKey', ui.ed_aliyun_productKey.text())
    save_params_local('ed_aliyun_device_name', ui.ed_aliyun_device_name.text())
    save_params_local('ed_aliyun_mac_sn', ui.ed_aliyun_mac_sn.text())
    save_params_local('ed_aliyun_device_secret', ui.ed_aliyun_device_secret.text())
    save_params_local('ed_aliyun_Region_Id', ui.ed_aliyun_Region_Id.currentIndex())


#  TCP UDP AT指令窗口 ------------------------------------------------------ STRAT  -------------------------------------
def initTCP_UDP_UI():
    ui.bt_tcp_udp_create.clicked.connect(OnclickTCPUDPCreate)
    ui.bt_tcp_udp_send_1.clicked.connect(OnclickSend1)
    ui.bt_tcp_udp_send_2.clicked.connect(OnclickSend2)
    ui.bt_tcp_udp_send_3.clicked.connect(OnclickSend3)
    ui.bt_tcp_udp_send_4.clicked.connect(OnclickSend4)
    ui.bt_tcp_udp_send_5.clicked.connect(OnclickSend5)
    ui.bt_tcp_udp_send_6.clicked.connect(OnclickSend6)
    ui.bt_tcp_udp_send_7.clicked.connect(OnclickSend7)
    ui.bt_tcp_udp_send_8.clicked.connect(OnclickSend8)
    ui.bt_tcp_udp_send_9.clicked.connect(OnclickSend9)
    ui.bt_tcp_udp_send_10.clicked.connect(OnclickSend10)


def OnclickSend1():
    ui.lineEdit_send_data.setText(ui.ed_tcp_udp_set_1.text())
    SendDataFuntion()


def OnclickSend2():
    ui.lineEdit_send_data.setText(ui.ed_tcp_udp_set_2.text())
    SendDataFuntion()


def OnclickSend3():
    ui.lineEdit_send_data.setText(ui.ed_tcp_udp_set_3.text())
    SendDataFuntion()


def OnclickSend4():
    ui.lineEdit_send_data.setText(ui.ed_tcp_udp_set_4.text())
    SendDataFuntion()


def OnclickSend5():
    ui.lineEdit_send_data.setText(ui.ed_tcp_udp_set_5.text())
    SendDataFuntion()


def OnclickSend6():
    ui.lineEdit_send_data.setText(ui.ed_tcp_udp_set_6.text())
    SendDataFuntion()


def OnclickSend7():
    ui.lineEdit_send_data.setText(ui.ed_tcp_udp_set_7.text())
    print("OnclickSend7", ui.cb_protocol_tcp_udp_boot.currentIndex())
    # 透传模式在FLASH？
    if ui.cb_protocol_tcp_udp_boot.currentIndex() == 1:
        SendDataFuntion(True)
    else:
        SendDataFuntion()


def OnclickSend8():
    ui.lineEdit_send_data.setText(ui.ed_tcp_udp_set_8.text())
    print("OnclickSend8", ui.cb_protocol_tcp_udp_boot.currentIndex())
    # 透传模式在FLASH？
    if ui.cb_protocol_tcp_udp_boot.currentIndex() == 0:
        SendDataFuntion(True)
    else:
        SendDataFuntion()


def OnclickSend9():
    ui.lineEdit_send_data.setText(ui.ed_tcp_udp_set_9.text())
    SendDataFuntion()


def OnclickSend10():
    ui.lineEdit_send_data.setText(ui.ed_tcp_udp_set_10.text())
    SendDataFuntion()


def OnclickTCPUDPCreate():
    # 获取本窗口的文本编辑框内容、按钮
    inputData = [ui.ed_tcp_udp_set_1, ui.ed_tcp_udp_set_2, ui.ed_tcp_udp_set_3,
                 ui.ed_tcp_udp_set_4, ui.ed_tcp_udp_set_5, ui.ed_tcp_udp_set_6,
                 ui.ed_tcp_udp_set_7, ui.ed_tcp_udp_set_8, ui.ed_tcp_udp_set_9, ui.ed_tcp_udp_set_10]
    desButton = [ui.bt_tcp_udp_send_1, ui.bt_tcp_udp_send_2, ui.bt_tcp_udp_send_3,
                 ui.bt_tcp_udp_send_4, ui.bt_tcp_udp_send_5, ui.bt_tcp_udp_send_6,
                 ui.bt_tcp_udp_send_7, ui.bt_tcp_udp_send_8, ui.bt_tcp_udp_send_9, ui.bt_tcp_udp_send_10]

    # TCP 不保存透传模式在FLASH？
    if ui.cb_protocol_tcp_udp_boot.currentIndex() == 0:
        isSaveInFlash = True
    else:
        isSaveInFlash = False

    # TCP 透传模式
    if ui.cb_protocol_tcp_udp.currentIndex() == 0:
        data = mEspMQTT.getTCP(isSaveInFlash, ui.ed_tcp_udp_broker.text(), ui.ed_tcp_udp_port.text(),
                               ui.ed_tcp_udp_ssid.text(), ui.ed_tcp_udp_password.text(), ui.ed_tcp_udp_content.text())
        for index in range(len(data['content'])):
            inputData[index].setText(data['content'][index])
        for index in range(len(data['des'])):
            desButton[index].setText(data['des'][index])

    # UDP 透传模式
    elif ui.cb_protocol_tcp_udp.currentIndex() == 1:
        data = mEspMQTT.getUDP(isSaveInFlash, ui.ed_tcp_udp_broker.text(), ui.ed_tcp_udp_port.text(),
                               ui.ed_tcp_udp_ssid.text(), ui.ed_tcp_udp_password.text(), ui.ed_tcp_udp_content.text())
        for index in range(len(data['content'])):
            inputData[index].setText(data['content'][index])
        for index in range(len(data['des'])):
            desButton[index].setText(data['des'][index])

    save_params_local("ed_tcp_udp_broker", ui.ed_tcp_udp_broker.text())
    save_params_local("ed_tcp_udp_port", ui.ed_tcp_udp_port.text())
    save_params_local("ed_tcp_udp_ssid", ui.ed_tcp_udp_ssid.text())
    save_params_local("ed_tcp_udp_password", ui.ed_tcp_udp_password.text())
    save_params_local("ed_tcp_udp_content", ui.ed_tcp_udp_content.text())
    save_params_local("cb_protocol_tcp_udp_boot", ui.cb_protocol_tcp_udp_boot.currentIndex())
    save_params_local("cb_protocol_tcp_udp", ui.cb_protocol_tcp_udp.currentIndex())


#  MQTT AT指令窗口 ------------------------------------------------------ STRAT  -------------------------------------
def initMqttUI():
    # mqtt create
    ui.bt_mqtt_create.clicked.connect(OnClickMqttCreate)
    # MQTT send
    ui.bt_mqtt_send_1.clicked.connect(OnclickMQTT1)
    ui.bt_mqtt_send_2.clicked.connect(OnclickMQTT2)
    ui.bt_mqtt_send_3.clicked.connect(OnclickMQTT3)
    ui.bt_mqtt_send_4.clicked.connect(OnclickMQTT4)
    ui.bt_mqtt_send_5.clicked.connect(OnclickMQTT5)
    ui.bt_mqtt_send_6.clicked.connect(OnclickMQTT6)
    ui.bt_mqtt_send_7.clicked.connect(OnclickMQTT7)
    ui.bt_mqtt_send_8.clicked.connect(OnclickMQTT8)


def OnClickMqttCreate():
    textUserName = ui.ed_username.text()
    textBroker = ui.ed_broker.text()
    textPort = ui.ed_port.text()
    textPassword = ui.ed_password.text()
    textClientId = ui.ed_clientId.text()
    textSSID = ui.ed_ssid.text()
    textSSIDPassword = ui.ed_SSIDpassword.text()
    inputData = [ui.ed_mqtt_set_1, ui.ed_mqtt_set_2, ui.ed_mqtt_set_3, ui.ed_mqtt_set_4, ui.ed_mqtt_set_5,
                 ui.ed_mqtt_set_6, ui.ed_mqtt_set_7, ui.ed_mqtt_set_8]
    desButton = [ui.bt_mqtt_send_1, ui.bt_mqtt_send_2, ui.bt_mqtt_send_3, ui.bt_mqtt_send_4, ui.bt_mqtt_send_5,
                 ui.bt_mqtt_send_6, ui.bt_mqtt_send_7, ui.bt_mqtt_send_8]

    data = mEspMQTT.getMQTT(textBroker, textUserName, textPort, textClientId, textPassword, textSSID, textSSIDPassword,
                            ui.ed_mqtt_sub_topic.text(),
                            ui.ed_mqtt_pub_topic.text(), ui.ed_mqtt_pub_msg.text())
    for index in range(len(data['content'])):
        inputData[index].setText(data['content'][index])
    for index in range(len(data['des'])):
        desButton[index].setText(data['des'][index])

    save_params_local('textMQTTBroker', ui.ed_broker.text())
    save_params_local('textMQTTPort', ui.ed_port.text())
    save_params_local('textMQTTUserName', ui.ed_username.text())
    save_params_local('textMQTTPassword', ui.ed_password.text())
    save_params_local('textMQTTClientId', ui.ed_clientId.text())
    save_params_local('textMQTTSubTopic', ui.ed_mqtt_sub_topic.text())
    save_params_local('textMQTTPubTopic', ui.ed_mqtt_pub_topic.text())
    save_params_local('textMQTTPubMsg', ui.ed_mqtt_pub_msg.text())
    save_params_local('textMQTTRouterSSID', ui.ed_ssid.text())
    save_params_local('textMQTTRouterPWD', ui.ed_SSIDpassword.text())


def OnclickMQTT1():
    print("init mqtt OnClickMqttCreate")
    ui.lineEdit_send_data.setText(ui.ed_mqtt_set_1.text())
    SendDataFuntion()


def OnclickMQTT2():
    ui.lineEdit_send_data.setText(ui.ed_mqtt_set_2.text())
    SendDataFuntion()


def OnclickMQTT3():
    ui.lineEdit_send_data.setText(ui.ed_mqtt_set_3.text())
    SendDataFuntion()


def OnclickMQTT4():
    ui.lineEdit_send_data.setText(ui.ed_mqtt_set_4.text())
    SendDataFuntion()


def OnclickMQTT5():
    ui.lineEdit_send_data.setText(ui.ed_mqtt_set_5.text())
    SendDataFuntion()


def OnclickMQTT6():
    ui.lineEdit_send_data.setText(ui.ed_mqtt_set_6.text())
    SendDataFuntion()


def OnclickMQTT7():
    ui.lineEdit_send_data.setText(ui.ed_mqtt_set_7.text())
    SendDataFuntion()


def OnclickMQTT8():
    ui.lineEdit_send_data.setText(ui.ed_mqtt_set_8.text())
    SendDataFuntion()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon("res/favicon.ico"))
    MainWindow = QMainMyWindow()
    ui = UI_Serial.Ui_AithinkerSerial()
    ui.setupUi(MainWindow)

    # 禁止拉伸窗口大小
    # MainWindow.setFixedSize(MainWindow.width(), MainWindow.height())
    # # !!!修复DesignerQT5自定义QWidget时候，window不会设置调用setCentralWidget设置在中心
    MainWindow.setCentralWidget(ui.centralwidget)
    # # 设置电脑键盘回调
    ui.centralwidget.set_connect_key_press(windows_key_press)
    dk = app.desktop()

    # 定时发送数据
    timer_send = QTimer()
    timer_send.timeout.connect(SendDataFuntion)

    #  初始化AT
    mATObj = AT()
    mATObj.set_default_at_result_callBack(at_callback_handler)

    mEspMQTT = Espressif()
    mAliYunMQTT = AliYun()
    InitUI()
    # 从上次记录获取面板设置显示
    load_from_local()
    # 居中显示
    # MainWindow.move((int)(dk.width() / 2 - MainWindow.width() / 2), (int)(dk.height() / 2 - MainWindow.height() / 2))
    _translate = QtCore.QCoreApplication.translate
    MainWindow.setWindowTitle(
        _translate("AithinkerSerial", "安信可模组串口调试助手 " + SOFTWARE_VERSION + " - By 安信可开源团队 半颗心脏 www.ai-tihinker.com"))
    MainWindow.show()

    refreshPort()
    sys.exit(app.exec_())
