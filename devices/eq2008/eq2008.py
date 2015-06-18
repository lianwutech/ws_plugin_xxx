#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
EQ2008库DLL的Ctypes封装
"""

from win32api import *
from ctypes import *

from libs.winutils import RGB


# 定义结构
# 面板区域结构定义
class _StructPartInfo(Structure):
    _fields_ = [('iX', c_int),
                ('iY', c_int),
                ('iWidth', c_int),
                ('iHeight', c_int),
                ('iFrameMode', c_int),
                ('FrameColor', c_int)]
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

# 发送数据
# DLL_API BOOL __stdcall User_SendToScreen(int CardNum);
api.User_SendToScreen.argtypes = [c_int]
api.User_SendToScreen.restype = c_bool

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
api.User_RealtimeSendData.argtypes = [c_int, c_int, c_int, c_int, c_int]
api.User_RealtimeSendData.restype = c_bool

# 断开连接
# DLL_API BOOL __stdcall User_RealtimeDisConnect(int CardNum);
api.User_RealtimeDisConnect.argtypes = [c_int]
api.User_RealtimeDisConnect.restype = c_bool


#初始化并登录
api.InitInterface(u"中心服务器地址" , u'上行服务端端口' , u'下行客户端端口')
api.Login(platformID,userID,password);
#.....其它操作
api.Logout(platformID,userID,password); #注销