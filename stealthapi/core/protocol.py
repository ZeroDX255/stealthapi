"""This module provides all the tools needed to establish a connection with
Stealth.
"""

__all__ = ['StealthConnection']

import asyncio
import ctypes
import logging
import threading
import time

from stealthapi.config import TIMER_RES
from stealthapi.core.packet import IncomingPacketCmdEnum, Packet, \
    PacketParseError
from stealthapi.core.utils import format_packet


class StealthConnection(asyncio.Protocol):
    """TODO"""

    _transport: asyncio.Transport  # socket transport
    _buffer: bytes  # storage for data parts

    _request_id: int  # a unique ident for every method returning result
    _pause: bool  # pause script

    _methods_responses: dict[int, bytes]

    _logger: logging.Logger

    def __init__(self) -> None:
        self._buffer = bytes()
        self._pause = False
        self._request_id = 0
        self._methods_responses = {}
        # init logger
        thread = threading.current_thread()
        logger_name = f'{self.__class__.__name__}-{thread.ident}'
        self._logger = logging.getLogger(logger_name)
        self._logger.debug('initialized')

    def __del__(self) -> None:
        # close socket before destroy the current instance
        self._transport.close()
        while self._transport.is_closing():
            time.sleep(TIMER_RES)
        self._logger.debug('connection closed')

    @property
    def request_id(self) -> int:
        """A unique request id for methods returning result."""
        self._request_id += 1
        if self._request_id >= ctypes.sizeof(ctypes.c_ushort) - 1:
            # reset value if greater than unsigned short max value
            self._request_id = 1
        return self._request_id

    @property
    def pause(self) -> bool:
        """True if the current script is on pause."""
        return self._pause

    def connection_made(self, transport: asyncio.Transport) -> None:
        self._transport = transport

    def send(self, data: bytes | bytearray) -> None:
        """Send the given data to Stealth."""
        self._transport.write(data)
        self._logger.debug(f'data sent: {format_packet(data)}')

    def data_received(self, data: bytes) -> None:
        """TODO"""
        self._logger.debug(f'data received: {format_packet(data)}')
        # parse packet
        self._buffer += data
        while 42:
            try:
                packet = Packet.unpack_from(self._buffer)
            except PacketParseError:
                break

            match packet.cmd:
                # method response
                case IncomingPacketCmdEnum.SC_METHOD_RESPONSE:
                    self._methods_responses[packet.request_id] = packet.data

                # event
                case IncomingPacketCmdEnum.EVENT:
                    pass  # TODO: events

                # pause script
                case IncomingPacketCmdEnum.PAUSE:
                    self._pause = not self._pause

                # terminate script
                case IncomingPacketCmdEnum.TERMINATE:
                    exit()

                # other
                case _:
                    self._logger.warning(f'Unknown packet type: {packet.cmd}')

            self._buffer = self._buffer[packet.size:]
