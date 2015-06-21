#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os
import time
import json
import cairo
import rsvg
from PIL import Image

def convert_svg_to_png(svg_file_name, png_file_name):
    file_svg = open(svg_file_name)
    svg_data = file_svg.read()
    img = cairo.ImageSurface(cairo.FORMAT_ARGB32, 640,480)
    ctx = cairo.Context(img)
    ## handle = rsvg.Handle(<svg filename>)
    # or, for in memory SVG data:
    handle = rsvg.Handle(None, str(svg_data))
    handle.render_cairo(ctx)
    img.write_to_png(png_file_name)

def convert_png_to_bmp(png_file_name, bmp_file_name):
    img_png = Image.open(png_file_name)
    try:
        # 使用白色来填充背景 from：www.sharejs.com
        # (alpha band as paste mask).
        length_x, length_y = img_png.size
        img = Image.new('RGBA', img_png.size, (255, 255, 255))
        img.paste(img_png, (0, 0, length_x, length_y), img_png)
        img.save("new_test.png")

        new_img = Image.open("new_test.png")
        # 转换成RGBA格式
        new_img.convert("RGBA")
        # 分割成RGBA，然后重新组合
        lenght = len(new_img.split())
        if len(new_img.split()) == 4:
            # prevent IOError: cannot write mode RGBA as BMP
            r, g, b, a = new_img.split()
            new_img = Image.merge("RGB", (r, g, b))
            new_img.save(bmp_file_name)
        else:
            new_img.save(bmp_file_name)
        print "convert success."
    except Exception,e :
        print "exception: %r" % e

svg_file_name = "test.svg"
png_file_name = "test.png"
bmp_file_name = "test.bmp"


convert_svg_to_png(svg_file_name, png_file_name)
convert_png_to_bmp(png_file_name, bmp_file_name)






