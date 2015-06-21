#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
EQ2008库DLL的Ctypes封装
"""

from ctypes import *
from ctypes.wintypes import *
import win32con
import win32gui

from libs.winutils import RGB


# 定义结构
# 面板区域结构定义
class _StructPartInfo(Structure):
    _fields_ = [('iX', c_int),
                ('iY', c_int),
                ('iWidth', c_int),
                ('iHeight', c_int),
                ('iFrameMode', c_int),
                ('FrameColor', COLORREF)]
    def __str__(self):
        return 'iX:%d, iY:%d, iWidth:%d, iHeight:%d, iFrameMode:%d, FrameColor:%d'.format(self.iX,
                                                                                          self.iY,
                                                                                          self.iWidth,
                                                                                          self.iHeight,
                                                                                          self.iFrameMode,
                                                                                          self.FrameColor)


# User_Bmp结构定义
class _StructUserBmp(Structure):
    _fields_ =[('PartInfo', _StructPartInfo)]
    def __str__(self):
        return 'User_PartInfo:%s'.format(self.User_PartInfo)


# 节目控制
class _StructMoveSet(Structure):
    _fields_ = [('iActionType', c_int),
                ('iActionSpeed', c_int),
                ('bClear', c_bool),
                ('iHoldTime', c_int),
                ('iClearSpeed', c_int),
                ('iClearActionType', c_int),
                ('iFrameTime', c_int)]
    def __str__(self):
        return """iActionType:%d, iActionSpeed:%d, bClear:%r, iHoldTime:%d, iClearSpeed:%d, iClearActionType:%d, iFrameTime:%d""".\
            format(self.iActionType,
                   self.iActionSpeed,
                   self.bClear,
                   self.iHoldTime,
                   self.iClearSpeed,
                   self.iClearActionType,
                   self.iFrameTime)

# dll的配置文件
eq2008_ini = "devices/eq2008/EQ2008_Dll_Set.ini"

#加载API库
api = CDLL('devices/eq2008/EQ2008_Dll.dll')

#初始化函数的参数类型
# 添加节目
# DLL_API int __stdcall User_AddProgram(int CardNum,BOOL bWaitToEnd,int iPlayTime);
api.User_AddProgram.argtypes = [c_int, c_bool, c_int]
api.User_AddProgram.restype = c_int

# 添加图文区
# DLL_API int  __stdcall User_AddBmpZone(int CardNum,User_Bmp *pBmp,int iProgramIndex);
api.User_AddBmpZone.argtypes = [c_ushort, _StructUserBmp, c_ushort]
api.User_AddBmpZone.restype = c_int

# DLL_API BOOL __stdcall User_AddBmp(int CardNum,int iBmpPartNum,HBITMAP hBitmap,User_MoveSet* pMoveSet,int iProgramIndex);
api.User_AddBmp.argtypes = [c_int, c_int, c_long, _StructMoveSet, c_int]
api.User_AddBmp.restype = c_bool

# DLL_API BOOL __stdcall User_AddBmpFile(int CardNum,int iBmpPartNum,char *strFileName,User_MoveSet* pMoveSet,int iProgramIndex);
api.User_AddBmpFile.argtypes = [c_int, c_int, c_char_p, _StructMoveSet, c_int]
api.User_AddBmpFile.restype = c_bool

# 删除节目
# DLL_API BOOL __stdcall User_DelProgram(int CardNum,int iProgramIndex);
api.User_DelProgram.argtypes = [c_int, c_int]
api.User_DelProgram.restype = c_bool

# 删除所有节目
# DLL_API BOOL __stdcall User_DelAllProgram(int CardNum);
api.User_DelAllProgram.argtypes = [c_int]
api.User_DelAllProgram.restype = c_bool

# 发送数据
# DLL_API BOOL __stdcall User_SendToScreen(int CardNum);
api.User_SendToScreen.argtypes = [c_int]
api.User_SendToScreen.restype = c_bool

# 发送节目文件和索引文件
# DLL_API BOOL __stdcall User_SendFileToScreen(int CardNum,char pSendPath[MAX_PATH],char pIndexPath[MAX_PATH]);
api.User_SendFileToScreen.argtypes = [c_int, c_char_p, c_char_p]
api.User_SendFileToScreen.restype = c_bool

# 开机
# DLL_API BOOL __stdcall User_OpenScreen(int CardNum);
api.User_OpenScreen.argtypes = [c_int]
api.User_OpenScreen.restype = c_bool

# 关机
# DLL_API BOOL __stdcall User_CloseScreen(int CardNum);
api.User_CloseScreen.argtypes = [c_int]
api.User_CloseScreen.restype = c_bool

# 校正板卡的时间
# DLL_API BOOL __stdcall User_AdjustTime(int CardNum);
api.User_AdjustTime.argtypes = [c_int]
api.User_AdjustTime.restype = c_bool

# 实时发送数据
# DLL_API BOOL __stdcall User_RealtimeConnect(int CardNum);	 //建立连接
api.User_RealtimeConnect.argtypes = [c_int]
api.User_RealtimeConnect.restype = c_bool

# 发送数据
# DLL_API BOOL __stdcall User_RealtimeSendData(int CardNum,int x,int y,int iWidth,int iHeight,HBITMAP hBitmap);
api.User_RealtimeSendData.argtypes = [c_int, c_int, c_int, c_int, HBITMAP]
api.User_RealtimeSendData.restype = c_bool

# 断开连接
# DLL_API BOOL __stdcall User_RealtimeDisConnect(int CardNum);
api.User_RealtimeDisConnect.argtypes = [c_int]
api.User_RealtimeDisConnect.restype = c_bool


def open_screan(card_num):
    result = api.User_OpenScreen(c_int(card_num))
    return result.value

# 直接发送BMP图片到LED
def send_bmp_to_led(card_num, height, weight, bmp_file):
    c_card_num = c_int(card_num)
    c_bmp_file = c_char_p(bmp_file)
    c_program_index = api.User_AddProgram(c_card_num)
    if c_program_index == 0:
        return False

    # 初始化区域
    c_bmp_zone = _StructUserBmp()
    c_bmp_zone.PartInfo.iX = c_int(0)
    c_bmp_zone.PartInfo.iY = c_int(0)
    c_bmp_zone.PartInfo.iWidth = c_int(weight)
    c_bmp_zone.PartInfo.iHeight = c_int(height)
    c_bmp_zone.PartInfo.iFrameMode = c_int(0xFF00)
    c_bmp_zone.PartInfo.FrameColor = COLORREF(RGB(0x00, 0xFF, 0x00))

    # 初始化图形移动设置
    c_move_set = _StructMoveSet()
    c_move_set.iActionType = c_int(0)
    c_move_set.iActionSpeed = c_int(4)
    c_move_set.bClear = c_bool(True)
    c_move_set.iHoldTime = c_int(50)
    c_move_set.iClearSpeed = c_int(4)
    c_move_set.iClearActionType = c_int(4)
    c_move_set.iFrameTime = c_int(20)

    # iBMPZoneNum = User_AddBmpZone(g_iCardNum, ref BmpZone, g_iProgramIndex);
    c_bmp_zone_num = api.User_AddBmpZone(c_card_num, byref(c_bmp_zone), c_program_index)

    # if (false == User_AddBmpFile(g_iCardNum, iBMPZoneNum, strBmpFile, ref MoveSet, g_iProgramIndex))
    if False == api.User_AddBmpFile(c_card_num, c_bmp_zone_num, c_bmp_file, byref(c_move_set), c_program_index):
        return False

    # Bitmap bmp  = new Bitmap(pictureBox2.Image,BmpZone.PartInfo.iWidth ,BmpZone.PartInfo.iHeight);
    icon_flags = win32con.LR_LOADFROMFILE | win32con.LR_DEFAULTSIZE
    h_bitmap = win32gui.LoadImage(0, c_bmp_file, win32con.IMAGE_BITMAP, 0, 0, icon_flags)

    # if (false == User_AddBmp(g_iCardNum, iBMPZoneNum,bmp.GetHbitmap() ,ref MoveSet, g_iProgramIndex))
    if -1 == api.User_AddBmp(c_card_num, c_bmp_zone_num, h_bitmap, byref(c_move_set), c_program_index):
        return False

    # 发送数据
    # if(User_SendToScreen(m_iCardNum)==FALSE)
    result = api.User_SendToScreen(c_card_num)
    return result.value

