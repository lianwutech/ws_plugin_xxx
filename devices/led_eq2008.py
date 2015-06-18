#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
LER EQ2008设备类
EQ2008设备协议。
参数配置说明：
device_id和cardnum的对应关系
如：
"device": {
    “device_1”: 0,
    "device_2": 1
  }
"""

import os
import time
import json
import logging
from Jinja2 import Template
import cairo
import rsvg
from PIL import Image

from libs.winutils import RGB
from libs.base_device import BaseDevice
from devices.eq2008 import eq2008

logger = logging.getLogger('plugin')

# 直接发送数据到LED
def send_bmp_to_led(card_num, height, weight):
    program_index = eq2008.api.User_AddProgram(card_num)
    if program_index == 0:
        return False

    # 初始化区域
    bmp_zone = eq2008._StructUserBmp()
    bmp_zone.PartInfo.iX = 0
    bmp_zone.PartInfo.iY = 0
    bmp_zone.PartInfo.iWidth = weight
    bmp_zone.PartInfo.iHeight = height
    bmp_zone.PartInfo.iFrameMode = 0xFF00
    bmp_zone.PartInfo.FrameColor = RGB(0x00, 0xFF, 0x00)

    # 初始化图形移动设置
    move_set = eq2008._StructMoveSet()
    move_set.iActionType = 0
    move_set.iActionSpeed = 4
    move_set.bClear = True
    move_set.iHoldTime = 50
    move_set.iClearSpeed = 4
    move_set.iClearActionType = 4
    move_set.iFrameTime = 20

    zone_num = eq2008.api.User_AddBmpZone(card_num, bmp_zone, program_index)


    pass

class LEDQE2008Device(BaseDevice):
    def __init__(self, device_params, devices_file_name, mqtt_client, network_name):
        BaseDevice.__init__(self, device_params, devices_file_name, mqtt_client, network_name)
        # 配置项
        self.server = device_params.get("server", "")
        self.port = device_params.get("port", 0)
        self.card_num = device_params.get("card_num", 0)
        self.svg_file_template = device_params.get("svg_file_template", "")
        self.mqtt_client = mqtt_client

    @staticmethod
    def check_config(device_params):
        if "server" not in device_params or "port" not in device_params:
            return False
        return BaseDevice.check_config(device_params)

    def run(self):
        # 首先上报设备数据
        for device_id in self.devices_info_dict:
            device_info = self.devices_info_dict[device_id]
            device_msg = {
                "device_id": device_info["device_id"],
                "device_type": device_info["device_type"],
                "device_addr": device_info["device_addr"],
                "device_port": device_info["device_port"],
                "protocol": "",
                "data": ""
            }
            self.mqtt_client.publish_data(device_msg)

        # 后续没有任何处理
        return

    def process_cmd(self, device_cmd_msg):
        device_id = device_cmd_msg.get("device_id", "")
        device_cmd = device_cmd_msg["command"]
        if device_id in self.devices_info_dict:
            device_info = self.devices_info_dict[device_id]
        else:
            logger.error("不支持的modbus指令：%r" % device_cmd)
            return

        # device_cmd为字符串
        output_data = json.loads(device_cmd)

        # 判断文件是否存在
        if not os.path.exists(self.svg_file_template):
            logger.error("svg template file(%s) not exist." % "")
            return

        # 根据配置项打开svg模版文件并基于模版文件和数据生成svg文件
        file_svg_template = open(self.svg_file_template)
        template_content = file_svg_template.read()
        svg_template = Template(template_content)
        svg_content = svg_template.render(output_data)
        img = cairo.ImageSurface(cairo.FORMAT_ARGB32, 640, 480)
        ctx = cairo.Context(img)
        handle= rsvg.Handle(None, str(svg_content))

        # svg文件生成png
        png_file_name = "%r.png" % device_id
        handle.render_cairo(ctx)
        img.write_to_png(png_file_name)

        # png文件生成bmp
        bmp_file_name = "%r.bmp" % device_id
        img = Image.open(png_file_name)
        new_img = img.resize((128, 128), Image.BILINEAR)
        new_img.save(bmp_file_name, "bmp")

        # bmp文件输出到LED

        # 输出图片
        pass

    def isAlive(self):
        return True