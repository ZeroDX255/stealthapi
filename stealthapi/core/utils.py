"""This module provides some useful utilities."""

__all__ = ['IS_WIN', 'ConnectionsContainer', 'get_connection_port',
           'get_event_loop', 'format_packet']

import asyncio
import logging
import platform
import struct
import threading
import types
from collections import Iterable

from stealthapi.config import ENDIAN, HOST, PORT
from stealthapi.core.protocol import StealthConnection as Protocol

IS_WIN = platform.system() == 'Windows'


class ConnectionsContainer:
    """This class is a simple storage for all active connections with Stealth.
    """

    _lock = threading.Lock
    _connections = {}  # { thread_ident: StealthConnection }

    def __init__(self):
        msg = "ConnectionsContainer class shouldn't have instances."
        raise RuntimeError(msg)

    @staticmethod
    def _join(self: threading.Thread, timeout: float | None = None) -> None:
        """This method should be injected to every thread."""
        ConnectionsContainer.disconnect(self.ident)
        self.__class__.join(self, timeout)

    # noinspection PyPropertyDefinition
    @classmethod
    @property
    async def connection(cls) -> Protocol:
        """Get a connections with Stealth for the current thread. Create a new
        one, if there is no StealthConnection instance for the current thread.
        """
        thread = threading.current_thread()
        with cls._lock:
            if thread.ident not in cls._connections:
                protocol = await cls._create_connection()
                cls._connections[thread.ident] = protocol

                # replace the join method for the current thread
                thread.join = types.MethodType(cls._join, thread)

            return cls._connections[thread.ident]

    @classmethod
    def disconnect(cls, thread_id: int) -> None:
        """Close connection with Stealth for the thread with the specified id.
        """
        with cls._lock:
            del cls._connections[thread_id]

    @staticmethod
    async def _create_connection():
        port = await get_connection_port()
        loop = get_event_loop()
        _, protocol = await loop.create_connection(Protocol, HOST, port)
        return protocol


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
    logger.debug(f'data sent: {format_packet}')

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
