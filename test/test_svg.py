#!/usr/bin/env python
# -*- coding:utf-8 -*-

import Image

im = Image.open("test.svg")

print im.format, im.size, im.mode

im.save("fileout.bmp", "bmp")










