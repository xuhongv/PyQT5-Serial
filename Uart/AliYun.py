import serial
import serial.tools.list_ports
from PyQt5.QtCore import QTimer, QObject
import asyncio
import time
from PyQt5.QtCore import pyqtSignal, QThread

import datetime
import time
import hmac
import hashlib
import math


class AliYun(QObject):

    def __init__(self):
        super(AliYun, self).__init__()

    def getAliYunMQTT(self, RegionId, ClientId, ProductKey, DeviceName, DeviceSecret):

        GET_CONTENT_ARRAY = []


        GET_CONTENT_DES_ARRAY = []
        Data = {}
        Data['des'] = GET_CONTENT_DES_ARRAY
        Data['content'] = GET_CONTENT_ARRAY

        # signmethod
        signmethod = "hmacsha1"

        # 当前时间毫秒值
        # us = math.modf(time.time())[0]
        # ms = int(round(us * 1000))
        # timestamp = str(ms)
        timestamp = '789'

        data = "".join(
            ("clientId", ClientId, "deviceName", DeviceName, "productKey", ProductKey, "timestamp", timestamp))
        # print(round((time.time() * 1000)))
        # print("data:", data)

        if "hmacsha1" == signmethod:
            ret = hmac.new(bytes(DeviceSecret, encoding="utf-8"),
                           bytes(data, encoding="utf-8"),
                           hashlib.sha1).hexdigest()
        elif "hmacmd5" == signmethod:
            ret = hmac.new(bytes(DeviceSecret, encoding="utf-8"),
                           bytes(data, encoding="utf-8"),
                           hashlib.md5).hexdigest()
        else:
            raise ValueError

        sign = ret
        print("sign:", sign)

        # ======================================================
        strBroker = ProductKey + ".iot-as-mqtt." + RegionId + ".aliyuncs.com"
        port = '1883'
        client_id = "".join((ClientId, "|securemode=3", ",signmethod=", signmethod, ",timestamp=", timestamp, "|"))
        username = "".join((DeviceName, "&", ProductKey))
        password = sign
        pubTopic = '/sys/' + ProductKey + "/" + DeviceName + "/thing/event/property/post"
        subTopic = '/sys/' + ProductKey + "/" + DeviceName + "/thing/event/property/post_reply"

        GET_CONTENT_ARRAY.append(strBroker)
        GET_CONTENT_ARRAY.append(port)
        GET_CONTENT_ARRAY.append(username)
        GET_CONTENT_ARRAY.append(password)
        GET_CONTENT_ARRAY.append(client_id)
        GET_CONTENT_ARRAY.append(subTopic)
        GET_CONTENT_ARRAY.append(pubTopic)

        # print("=")
        # print("strBroker:", strBroker)
        # print("client_id:", client_id)
        # print("port:", port)
        # print("username:", username)
        # print("password:", password)
        # print("pubTopic:", pubTopic)
        # print("subTopic:", subTopic)
        # print("=")

        return Data
