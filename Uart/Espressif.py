import serial
import serial.tools.list_ports
from PyQt5.QtCore import QTimer, QObject
import asyncio
import re
from PyQt5.QtCore import pyqtSignal, QThread


class Espressif(QObject):

    def __init__(self):
        super(Espressif, self).__init__()

    # 对应文档 https://docs.espressif.com/projects/esp-at/zh_CN/latest/AT_Command_Set/MQTT_AT_Commands.html
    def getMQTT(self, textBroker, textUserName, textPort, textClientId, textPassword, textSSID, textSSIDPassword
                , ed_mqtt_sub_topic, ed_mqtt_pub_topic, ed_mqtt_pub_msg):

        textUserName = eval(repr(eval(repr(textUserName).replace('\\', '\\\\'))).replace(',', '\\,'))
        textClientId = eval(repr(eval(repr(textClientId).replace('\\', '\\\\'))).replace(',', '\\,'))
        textClientId = eval(repr(eval(repr(textClientId).replace('\\', '\\\\'))).replace(',', '\\,'))
        textPassword = eval(repr(eval(repr(textPassword).replace('\\', '\\\\'))).replace(',', '\\,'))
        textSSID = eval(repr(eval(repr(textSSID).replace('\\', '\\\\'))).replace(',', '\\,'))
        textSSIDPassword = eval(repr(eval(repr(textSSIDPassword).replace('\\', '\\\\'))).replace(',', '\\,'))
        ed_mqtt_sub_topic = eval(repr(eval(repr(ed_mqtt_sub_topic).replace('\\', '\\\\'))).replace(',', '\\,'))
        ed_mqtt_pub_topic = eval(repr(eval(repr(ed_mqtt_pub_topic).replace('\\', '\\\\'))).replace(',', '\\,'))
        ed_mqtt_pub_msg = eval(repr(eval(repr(ed_mqtt_pub_msg).replace('\\', '\\\\'))).replace(',', '\\,'))

        GET_CONTENT_ARRAY = []
        GET_CONTENT_ARRAY.append('AT+CWMODE=1')
        GET_CONTENT_ARRAY.append('AT+CWJAP="' + textSSID + '","' + textSSIDPassword + '"')
        GET_CONTENT_ARRAY.append(
            'AT+MQTTUSERCFG=0,1,"' + textClientId + '","' + textUserName + '","' + textPassword + '",0,0,""')
        GET_CONTENT_ARRAY.append('AT+MQTTCONN=0,"' + textBroker + '",' + textPort + ',0')
        GET_CONTENT_ARRAY.append('AT+MQTTSUB=0,"' + ed_mqtt_sub_topic + '",0')
        GET_CONTENT_ARRAY.append('AT+MQTTPUB=0,"' + ed_mqtt_pub_topic + '","' + ed_mqtt_pub_msg + '",1,0')
        GET_CONTENT_ARRAY.append('AT+MQTTUNSUB=0,"' + ed_mqtt_sub_topic + '"')
        GET_CONTENT_ARRAY.append('AT+MQTTCLEAN=0')

        GET_CONTENT_DES_ARRAY = []
        GET_CONTENT_DES_ARRAY.append('设置STA模式')
        GET_CONTENT_DES_ARRAY.append('连接路由器')
        GET_CONTENT_DES_ARRAY.append('配置服务器')
        GET_CONTENT_DES_ARRAY.append('连接服务器')
        GET_CONTENT_DES_ARRAY.append("订阅主题")
        GET_CONTENT_DES_ARRAY.append("发布消息")
        GET_CONTENT_DES_ARRAY.append('取消订阅主题')
        GET_CONTENT_DES_ARRAY.append('断开服务器')
        Data = {}
        Data['des'] = GET_CONTENT_DES_ARRAY
        Data['content'] = GET_CONTENT_ARRAY
        return Data

    def getTCP(self, isSaveInFlash, tcp_udp_broker, ed_tcp_udp_port, textSSID, textSSIDPassword, content):

        tcp_udp_broker = eval(repr(eval(repr(tcp_udp_broker).replace('\\', '\\\\'))).replace(',', '\\,'))
        textSSID = eval(repr(eval(repr(textSSID).replace('\\', '\\\\'))).replace(',', '\\,'))
        textSSIDPassword = eval(repr(eval(repr(textSSIDPassword).replace('\\', '\\\\'))).replace(',', '\\,'))
        content = eval(repr(eval(repr(content).replace('\\', '\\\\'))).replace(',', '\\,'))

        Data = {}

        GET_CONTENT_ARRAY = []
        GET_CONTENT_ARRAY.append('AT+CWMODE=1')
        GET_CONTENT_ARRAY.append('AT+CWJAP="' + textSSID + '","' + textSSIDPassword + '"')
        GET_CONTENT_ARRAY.append('AT+CIPSTART="TCP","' + tcp_udp_broker + '",' + ed_tcp_udp_port)
        if isSaveInFlash:
            GET_CONTENT_ARRAY.append("AT+SAVETRANSLINK=1,\"" + tcp_udp_broker + '",' + ed_tcp_udp_port + ',\"TCP\"')
        GET_CONTENT_ARRAY.append("AT+CIPMODE=1")
        GET_CONTENT_ARRAY.append("AT+CIPSEND")
        GET_CONTENT_ARRAY.append(content)
        GET_CONTENT_ARRAY.append("+++")
        GET_CONTENT_ARRAY.append("AT+CIPCLOSE")
        # 兼容显示问题
        if not isSaveInFlash:
            GET_CONTENT_ARRAY.append("")

        GET_CONTENT_DES_ARRAY = []
        GET_CONTENT_DES_ARRAY.append('设置STA模式')
        GET_CONTENT_DES_ARRAY.append('连接路由器')
        GET_CONTENT_DES_ARRAY.append('连接服务器')
        if isSaveInFlash:
            GET_CONTENT_DES_ARRAY.append("设置开机透传")
        GET_CONTENT_DES_ARRAY.append("设置透传")
        GET_CONTENT_DES_ARRAY.append("开始透传")
        GET_CONTENT_DES_ARRAY.append('发送内容')
        GET_CONTENT_DES_ARRAY.append('退出透传')
        GET_CONTENT_DES_ARRAY.append('关闭连接')
        # 兼容显示问题
        if not isSaveInFlash:
            GET_CONTENT_DES_ARRAY.append("9")

        Data['des'] = GET_CONTENT_DES_ARRAY
        Data['content'] = GET_CONTENT_ARRAY
        return Data

    def getUDP(self, isSaveInFlash, tcp_udp_broker, ed_tcp_udp_port, textSSID, textSSIDPassword, content):

        tcp_udp_broker = eval(repr(eval(repr(tcp_udp_broker).replace('\\', '\\\\'))).replace(',', '\\,'))
        textSSID = eval(repr(eval(repr(textSSID).replace('\\', '\\\\'))).replace(',', '\\,'))
        textSSIDPassword = eval(repr(eval(repr(textSSIDPassword).replace('\\', '\\\\'))).replace(',', '\\,'))
        content = eval(repr(eval(repr(content).replace('\\', '\\\\'))).replace(',', '\\,'))

        Data = {}
        GET_CONTENT_ARRAY = []
        GET_CONTENT_ARRAY.append('AT+CWMODE=1')
        GET_CONTENT_ARRAY.append('AT+CWJAP="' + textSSID + '","' + textSSIDPassword + '"')
        GET_CONTENT_ARRAY.append('AT+CIPSTART="UDP","' + tcp_udp_broker + '",' + ed_tcp_udp_port)
        if isSaveInFlash:
            GET_CONTENT_ARRAY.append("AT+SAVETRANSLINK=1,\"" + tcp_udp_broker + '",' + ed_tcp_udp_port + ',\"UDP\"')
        GET_CONTENT_ARRAY.append("AT+CIPMODE=1")
        GET_CONTENT_ARRAY.append("AT+CIPSEND")
        GET_CONTENT_ARRAY.append(content)
        GET_CONTENT_ARRAY.append("+++")
        GET_CONTENT_ARRAY.append("AT+CIPCLOSE")
        # 兼容显示问题
        if not isSaveInFlash:
            GET_CONTENT_ARRAY.append("")

        GET_CONTENT_DES_ARRAY = []
        GET_CONTENT_DES_ARRAY.append('设置STA模式')
        GET_CONTENT_DES_ARRAY.append('连接路由器')
        GET_CONTENT_DES_ARRAY.append('连接服务器')
        if isSaveInFlash:
            GET_CONTENT_DES_ARRAY.append("设置开机透传")
        GET_CONTENT_DES_ARRAY.append("设置透传")
        GET_CONTENT_DES_ARRAY.append("开始透传")
        GET_CONTENT_DES_ARRAY.append('发送内容')
        GET_CONTENT_DES_ARRAY.append('退出透传')
        GET_CONTENT_DES_ARRAY.append('关闭连接')
        # 兼容显示问题
        if not isSaveInFlash:
            GET_CONTENT_DES_ARRAY.append("9")

        Data['des'] = GET_CONTENT_DES_ARRAY
        Data['content'] = GET_CONTENT_ARRAY
        return Data
