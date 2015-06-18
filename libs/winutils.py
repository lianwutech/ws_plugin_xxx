#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os
import sys
import json


def RGB(r, g, b):
    """
    COLORREF 映射
    COLORREF is a typedef to DWORD, not a structure.
    All RGB macro does is some bitshifting to get 0x00bbggrr value.
    :param r: red
    :param g: green
    :param b: blue
    :return:
    """
    r = r & 0xFF
    g = g & 0xFF
    b = b & 0xFF
    return (b << 16) | (g << 8) | r
