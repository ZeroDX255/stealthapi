"""
This module provides tools for working with high precision Windows media timers.
Got from https://stackoverflow.com/a/38488544
"""

__all__ = ['set_timer_resolution']

import contextlib
import ctypes.wintypes

dll = ctypes.WinDLL('winmm')


class TIMECAPS(ctypes.Structure):
    """
    https://docs.microsoft.com/en-us/windows/win32/api/timeapi/ns-timeapi-timecaps
    """
    _fields_ = (('wPeriodMin', ctypes.wintypes.UINT),
                ('wPeriodMax', ctypes.wintypes.UINT))

    @property
    def pointer(self):
        return ctypes.byref(self)

    @property
    def size(self):
        return ctypes.sizeof(self)


timeGetDevCaps = dll.timeGetDevCaps
timeGetDevCaps.argtypes = [ctypes.POINTER(TIMECAPS),  # ptc
                           ctypes.wintypes.UINT]  # cbtc

timeBeginPeriod = dll.timeBeginPeriod
timeBeginPeriod.argtypes = ctypes.wintypes.UINT,  # uPeriod

timeEndPeriod = dll.timeEndPeriod
timeEndPeriod.argtypes = ctypes.wintypes.UINT,  # uPeriod


@contextlib.contextmanager
def set_timer_resolution(resolution: int = 0) -> None:
    # get the lowest resolution
    caps = TIMECAPS()
    timeGetDevCaps(caps.pointer, caps.size)
    resolution = min(max(resolution, caps.wPeriodMin), caps.wPeriodMax)

    timeBeginPeriod(resolution)  # set resolution
    try:
        yield
    finally:
        timeEndPeriod(resolution)  # clear resolution
