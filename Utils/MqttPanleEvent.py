from PyQt5.QtCore import *
from PyQt5.QtGui import QTextCursor


class MqttPanleEvent:

    def getMQTT(self, textBroker, textUserName, textPort, textClientId, textPassword, textSSID, textSSIDPassword
                , ed_mqtt_sub_topic, ed_mqtt_pub_topic, ed_mqtt_pub_msg):
        GET_PORT_ARRAY = []
        GET_PORT_ARRAY.append('AT+CWMODE=1')
        GET_PORT_ARRAY.append('AT+CWJAP="' + textSSID + '","' + textSSIDPassword + '"')
        GET_PORT_ARRAY.append(
            'AT+MQTTUSERCFG=0,1,"' + textClientId + '","' + textUserName + '","' + textPassword + '",0,0,""')
        GET_PORT_ARRAY.append('AT+MQTTCONN=0,"' + textBroker + '",' + textPort + ',0')
        GET_PORT_ARRAY.append('AT+MQTTSUB=0,"' + ed_mqtt_sub_topic + '",0')
        GET_PORT_ARRAY.append('AT+MQTTPUB=0,"' + ed_mqtt_pub_topic + '","' + ed_mqtt_pub_msg + '",1,0')
        return GET_PORT_ARRAY


