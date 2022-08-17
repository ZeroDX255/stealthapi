"""This module provides some useful utilities."""

__all__ = ['sleep', 'get_connection_port', 'get_event_loop', 'format_packet']
import asyncio
import logging
import platform
import struct
from typing import Iterable

from stealthapi.config import ENDIAN, HOST, PORT
from stealthapi.core.winmm import set_timer_resolution

_IS_WIN = platform.system() == 'Windows'


async def sleep(msec: int) -> None:
    """Coroutine that completes after a given time (in milliseconds)."""
    # if windows - use high precision timers
    if _IS_WIN:
        with set_timer_resolution():
            await asyncio.sleep(msec)
    else:
        await asyncio.sleep(msec)


async def get_connection_port() -> int:
    """Request a port number from Stealth port provider server to create a new
    connection.

    :return: A port number
    """
    logger = logging.getLogger('get_port')
    get_port_packet = struct.pack(ENDIAN + 'HI', 4, 0xDEADBEEF)
    get_port_packet_response_struct = struct.Struct(ENDIAN + '2H')

    # connect to port provider server
    logger.debug(f'connecting to {HOST}:{PORT}')
    try:
        reader, writer = await asyncio.open_connection(HOST, PORT)
    except (ConnectionError, ConnectionRefusedError):
        logger.error("Can't connect to Stealth")
        raise

    # send the request port data
    writer.write(get_port_packet)
    logger.debug(f'data sent: {format_packet(get_port_packet)}')

    # receive port from Stealth
    _buffer = bytes()
    while 42:
        data = await reader.read(get_port_packet_response_struct.size)
        logger.debug(f'data received: {format_packet(data)}')
        _buffer += data
        try:
            _, port = get_port_packet_response_struct.unpack(_buffer)
            logger.debug(f'port: {port}')

            # close connection
            writer.close()
            await writer.wait_closed()
            logger.debug('connection closed')
            return port
        except struct.error:
            pass


def get_event_loop() -> asyncio.AbstractEventLoop:
    """Return the running event loop or create a new one.

    :return: an event loop
    """
    try:
        return asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.new_event_loop()


def format_packet(data: bytes | bytearray | Iterable[int], ) -> str:
    """Convert binary data to human-friendly format.

    :Example:
    >>>  format_packet(b'hello')
    68 65 6C 6C 6F

    :param data: any byte sequence
    :return: a pretty representation of the given binary data
    """
    return ' '.join([f'{x:02X}' for x in data])
