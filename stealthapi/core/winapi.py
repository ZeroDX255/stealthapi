"""
This module provides some wrapped windows functions and structures required to
establish a connection with Stealth.
"""

import ctypes
from ctypes.wintypes import *

FM_GETFOCUS = 0x600
PM_REMOVE = 0x1
WM_COPYDATA = 0x4A
PVOID = ctypes.c_char_p
ULONG_PTR = LPARAM
LRESULT = LPARAM


class COPYDATASTRUCT(ctypes.Structure):
    """Wraps COPYDATASTRUCT structure."""

    _fields_ = [('dwData', ULONG_PTR),
                ('cbData', DWORD),
                ('lpData', PVOID)]

    @property
    def ref(self):
        """Returns a pointer for the structure."""
        return ctypes.byref(self)


GetCurrentProcessId = ctypes.windll.kernel32.GetCurrentProcessId
GetCurrentProcessId.restype = DWORD

GetCurrentThreadId = ctypes.windll.kernel32.GetCurrentThreadId
GetCurrentThreadId.restype = DWORD

GetLastError = ctypes.windll.kernel32.GetLastError
GetLastError.restype = DWORD

FindWindow = ctypes.windll.user32.FindWindowW
FindWindow.restype = HWND
FindWindow.argtypes = (LPCWSTR,  # _In_opt_ lpClassName
                       LPCWSTR)  # _In_opt_ lpWindowName

MessageBox = ctypes.windll.user32.MessageBoxW
MessageBox.restype = INT
MessageBox.argtypes = (HWND,  # _In_opt_ hWnd
                       LPCWSTR,  # _In_opt_ lpText
                       LPCWSTR,  # _In_opt_ lpCaption
                       UINT)  # _In_ uType

PeekMessage = ctypes.windll.user32.PeekMessageW
PeekMessage.restype = BOOL
PeekMessage.argtypes = (LPMSG,  # _Out_ lpMsg
                        HWND,  # _In_opt_ hWnd
                        UINT,  # _In_ wMsgFilterMin
                        UINT,  # _In_ wMsgFilterMax
                        UINT)  # _In_ wRemoveMsg

SendMessage = ctypes.windll.user32.SendMessageW
SendMessage.restype = LRESULT
SendMessage.argtypes = (HWND,  # _In_ hWnd
                        UINT,  # _In_ Msg
                        WPARAM,  # _In_ wParam
                        ctypes.c_void_p)  # _In_ lParam

SetLastError = ctypes.windll.kernel32.SetLastError
SetLastError.argtypes = DWORD,  # _In_ dwErrCode
