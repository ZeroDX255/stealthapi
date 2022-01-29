"""This module provides the Packet class."""

__all__ = ['IncomingPacketCmdEnum', 'Packet', 'PacketParseError',
           'packet_size_struct', 'packet_cmd_struct', 'packet_id_struct']

import enum
import logging
import struct

from stealthapi.core.commands import \
    SC_METHOD_RESPONSE, \
    SC_PAUSE_SCRIPT, \
    SC_EVENT_CALLBACK, \
    SC_TERMINATE_SCRIPT
from stealthapi.config import ENDIAN


@enum.unique
class IncomingPacketCmdEnum(enum.Enum):
    RESPONSE = SC_METHOD_RESPONSE
    PAUSE = SC_PAUSE_SCRIPT
    EVENT = SC_EVENT_CALLBACK
    TERMINATE = SC_TERMINATE_SCRIPT


packet_size_struct = struct.Struct(ENDIAN + 'I')
packet_cmd_struct = struct.Struct(ENDIAN + 'H')
packet_id_struct = struct.Struct(ENDIAN + 'H')


class PacketParseError(Exception):
    """Raised when the data sequence length is not enough to unpack packet."""
    pass


class Packet:
    """This class represents a data packet incoming from Stealth."""

    _cmd: IncomingPacketCmdEnum
    _size: int
    _data: bytes | bytearray
    _request_id: int | None

    def __init__(self, cmd: IncomingPacketCmdEnum, size: int,
                 data: bytes | bytearray, request_id: int = None) -> None:
        self._cmd = cmd
        self._size = size
        self._data = data
        self._request_id = request_id

    @property
    def cmd(self) -> IncomingPacketCmdEnum:
        return self._cmd

    @property
    def size(self) -> int:
        return self._size

    @property
    def data(self) -> bytes | bytearray:
        return self._data

    @property
    def request_id(self) -> int | None:
        return self._request_id

    @classmethod
    def unpack_from(cls, buffer: bytes | bytearray) -> 'Packet':
        """Try to parse packet from the given bytes sequence.

        :Example:
        >>> import struct
        >>> from stealthapi.core.packet import Packet, PacketParseError
        >>> buf = struct.pack('<IHHI', 8, 14, 0x12345678)  # GetSelfId response
        >>> try: packet = Packet.unpack_from()
        >>> except PacketParseError: pass

        :param buffer: bytes sequence
        :return: a Packet-class instance
        :raises PacketParseError: if there is not enough bytes in the given data
        """
        # try to parse packet size first
        try:
            size, = packet_size_struct.unpack_from(buffer)
            offset = packet_size_struct.size
            data = buffer[offset:offset + size]
        except struct.error:
            msg = f'Not enough data to unpack size: {len(buffer)}'
            _logger.debug(msg)
            raise PacketParseError(msg)

        # parse header of the packet
        offset = 0
        request_id = None
        cmd, = packet_cmd_struct.unpack_from(data)
        offset += packet_cmd_struct.size

        # if method response - also parse request id
        if cmd == IncomingPacketCmdEnum.RESPONSE:
            request_id = packet_id_struct.unpack_from(data, offset)
            offset += packet_id_struct.size
        return cls(cmd, size + 4, data[offset:], request_id)


_logger = logging.getLogger(Packet.__class__.__name__)
