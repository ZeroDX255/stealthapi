"""This module provides some useful utilities."""

__all__ = ['IS_WIN', 'format_packet', 'get_event_loop']

import asyncio
import platform
from collections import Iterable

IS_WIN = platform.system() == 'Windows'


def format_packet(data: bytes | bytearray | Iterable[int], ) -> str:
    """Convert binary data to human-friendly format.

    :Example:
    >>>  format_packet(b'hello')
    68 65 6C 6C 6F

    :param data: any byte sequence
    :return: a pretty representation of the given binary data
    """
    return ' '.join([f'{x:02X}' for x in data])


def get_event_loop() -> asyncio.AbstractEventLoop:
    """Return the running event loop or create a new one.

    :return: an event loop
    """
    try:
        return asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.new_event_loop()
