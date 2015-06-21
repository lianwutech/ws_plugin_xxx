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

from libs.base_device import BaseDevice
from devices.eq2008 import eq2008

logger = logging.getLogger('plugin')

class LEDQE2008Device(BaseDevice):
    def __init__(self, device_params, devices_file_name, mqtt_client, network_name):
        BaseDevice.__init__(self, device_params, devices_file_name, mqtt_client, network_name)
        # 配置项
        self.server = device_params.get("server", "")
        self.port = device_params.get("port", 0)
        self.card_num = device_params.get("card_num", 0)
        self.height = device_params.get("height", 0)
        self.weight = device_params.get("weigth", 0)
        self.svg_file_template = device_params.get("svg_file_template", "")
        self.mqtt_client = mqtt_client

        # 打开屏幕
        eq2008.api.User_OpenScreen(self.card_num)

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
        svg_img = cairo.ImageSurface(cairo.FORMAT_ARGB32, 640, 480)
        ctx = cairo.Context(svg_img)
        handle = rsvg.Handle(None, str(svg_content))

        # svg文件生成png
        png_file_name = "%r.png" % device_id
        handle.render_cairo(ctx)
        svg_img.write_to_png(png_file_name)

        # png文件增加白色背景
        new_png_file_name = "new_%r.png" % device_id
        png_img = Image.open(png_file_name)
        length_x, length_y = png_img.size
        white_bg_img = Image.new('RGBA', png_img.size, (255, 255, 255))
        white_bg_img.paste(png_img, (0, 0, length_x, length_y), png_img)
        white_bg_img.save(new_png_file_name)

        # png文件生成bmp
        bmp_file_name = "%r.bmp" % device_id
        new_png_img = Image.open(new_png_file_name)
        # 转换成RGBA格式
        new_png_img.convert("RGBA")
        # 分割成RGBA，然后重新组合
        lenght = len(new_png_img.split())
        if len(new_png_img.split()) == 4:
            # prevent IOError: cannot write mode RGBA as BMP
            r, g, b, a = new_png_img.split()
            bmp_img = Image.merge("RGB", (r, g, b))
            bmp_img.save(bmp_file_name)
        else:
            new_png_img.save(bmp_file_name)

        # bmp文件输出到LED
        try:
            result = eq2008.send_bmp_to_led(self.card_num, self.height, self.weight, bmp_file_name)
            if result:
                logger.debug("outpu bmp %s success." % bmp_file_name)
            else:
                logger.debug("outpu bmp %s fail." % bmp_file_name)
        except Exception, e:
            logger.error("send_bmp_to_led exception: %r" % e)

    def isAlive(self):
        return True