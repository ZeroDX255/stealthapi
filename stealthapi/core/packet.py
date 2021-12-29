"""TODO"""

__all__ = ['Packet', 'PacketParseError']

import logging
import struct

from .commands import SC_METHOD_RESPONSE
from ..config import DEBUG, ENDIAN

_packet_size_struct = struct.Struct(ENDIAN + 'I')
_packet_cmd_struct = struct.Struct(ENDIAN + 'H')
_packet_id_struct = struct.Struct(ENDIAN + 'H')


class PacketParseError(Exception):
    """Raised when the data sequence length is not enough to unpack packet."""
    pass


class Packet:
    """TODO"""

    _cmd: int
    _size: int
    _data: bytes | bytearray
    _request_id: int | None

    def __init__(self, cmd: int, size: int, data: bytes | bytearray,
                 request_id: int = None) -> None:
        self._cmd = cmd
        self._size = size
        self._data = data
        self._request_id = request_id

    @property
    def cmd(self) -> int:
        """TODO"""
        return self._cmd

    @property
    def size(self) -> int:
        """TODO"""
        return self._size

    @property
    def data(self) -> bytes | bytearray:
        """TODO"""
        return self._data

    @property
    def request_id(self) -> int | None:
        """TODO"""
        return self._request_id

    @classmethod
    def unpack_from(cls, buffer: bytes | bytearray) -> 'Packet':
        """TODO"""
        try:
            size, = _packet_size_struct.unpack_from(buffer)
            offset = _packet_size_struct.size
            data = buffer[offset:offset + size]
        except struct.error:
            msg = f'Not enough data to unpack size: {len(buffer)}'
            if DEBUG:
                _logger.debug(msg)
            raise PacketParseError(msg)

        offset = 0
        request_id = None
        cmd, = _packet_cmd_struct.unpack_from(data)
        offset += _packet_cmd_struct.size
        if cmd == SC_METHOD_RESPONSE:
            request_id = _packet_id_struct.unpack_from(data, offset)
            offset += _packet_id_struct.size
        return cls(cmd, size + 4, data[offset:], request_id)


_logger = logging.Logger(Packet.__class__.__name__)
