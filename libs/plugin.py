#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
插件通用库
"""
import os
import json
import logging

from libs.utils import *
from libs.base_device import BaseDevice

# 日志处理
logger = logging.getLogger('plugin')

# 获取配置项
def load_config(config_file_name):
    if os.path.exists(config_file_name):
        config_file = open(config_file_name, "r+")
        content = config_file.read()
        config_file.close()
        try:
            config_info = convert(json.loads(content.encode("utf-8")))
            logger.debug("load config info success，%s" % content)
            return config_info
        except Exception, e:
            logger.error("load config info fail，%r" % e)
            return None
    else:
        logger.error("config file is not exist. Please check!")
        return None


# 加载Device类
def load_device(device_type):
    device_type = device_type.lower()
    # 扫描通道库
    # 通过扫描目录来获取支持的协议库
    cur_dir = cur_file_dir()
    if cur_dir is not None:
        device_lib_path = cur_dir + "/devices"
        file_list = os.listdir(device_lib_path)
        for file_name in file_list:
            file_path = os.path.join(device_lib_path, file_name)
            if os.path.isfile(file_path) and device_type + ".py" == file_name:
                device_name, ext = os.path.splitext(file_name)
                # 确保协议名称为小写
                device_name = device_name.lower()
                # 加载库
                module_name = "devices." + device_name
                try:
                    module = __import__(module_name)
                    device_module_attrs = getattr(module, device_name)
                    class_object = get_subclass(device_module_attrs, BaseDevice)
                    return class_object
                except Exception, e:
                    logger.error("Load device(%s) fail, error info:%r" % (module_name, e))
    return None