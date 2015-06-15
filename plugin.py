#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
    modbus网络的串口数据采集插件
    1、device_id的组成方式为ip_port_slaveid
    2、设备类型为0，协议类型为modbus
    3、devices_info_dict需要持久化设备信息，启动时加载，变化时写入
    4、device_cmd内容：json字符串
"""

import time

from setting import *
from libs.plugin import *
from libs.mqttclient import MQTTClient

# 全局变量
devices_file_name = "devices.txt"
config_file_name = "plugin.cfg"

# 日志对象
logger = logging.getLogger('plugin')

# 配置信息
config_info = load_config(config_file_name)


