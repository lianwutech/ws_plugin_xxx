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

# 停止标记
run_flag = False

def plugin_stop():
    """
    插件停止
    :return:
    """
    run_flag = False

def plugin_run():
    """
    插件运行主函数
    :return:
    """
    # 连接mqtt
    # 连接设备
    #

    run_flag = True

    # 切换工作目录
    os.chdir(cur_file_dir())

    if "device_type" not in config_info \
            or "mqtt" not in config_info \
            or "device" not in config_info \
            or "protocol" not in config_info:
        logger.fatal("配置文件配置项不全，启动失败。")
        return

    device_type = config_info["device_type"]
    network_name = config_info["network_name"]

    # 获取Device类对象
    device_class = load_device(device_type)

    # 参数检查
    if device_class.check_config(config_info["device"]) \
            and MQTTClient.check_config(config_info["mqtt"]):
        logger.debug("参数检查通过。")
    else:
        logger.fatal("device、protocol、mqtt参数配置项错误，请检查.")
        return

    # 此处需注意启动顺序，先创建mqtt对象，然后创建device对象，mqtt对象设置device属性，mqtt才能够链接服务器
    # 1、初始化mqttclient对象
    mqtt_client = MQTTClient(config_info["mqtt"], network_name)
    result = mqtt_client.connect()
    if not result:
        logger.fatal("mqtt connect fail.")
        return

    # 3、初始化device对象
    device = device_class(config_info["device"], devices_file_name, mqtt_client, network_name)

    # 4、mqtt设置通道对象
    mqtt_client.set_device(device)

    while True:
        if not device.isAlive():
            logger.info("device进程停止，重新启动。")
            device.start()

        if not mqtt_client.isAlive():
            logger.info("mqtt进程停止，重新启动。")
            mqtt_client.start()

        logger.debug("周期处理结束")
        time.sleep(2)

