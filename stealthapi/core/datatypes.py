"""
This module provides classes that convert delphi data types.
"""

import abc
import struct
import sys
from typing import Optional, Union

__all__ = ['_bool', '_char', '_byte', '_ubyte', '_short', '_ushort', '_int',
           '_uint', '_float', '_double', '_long', '_ulong', '_str', '_buffer']

CODEC: str = 'utf-16le' if sys.byteorder == 'little' else 'utf-16be'
UNICODE_CHAR_LENGTH = len('s'.encode(CODEC))

# typing
Numeric = Union[int, float]


class _DataTypeMeta(type):
    """Creates s struct.Struct instance for every data type class."""

    def __init__(cls, name, args, kwargs):
        super(_DataTypeMeta, cls).__init__(name, args, kwargs)
        cls._struct = struct.Struct(kwargs['_format'])
        cls._max_value = 2 ** (cls._struct.size * 8) - 1


class NumericBase(metaclass=abc.ABCMeta):
    """Base class for all numeric data type classes."""

    _struct: struct.Struct = None
    _max_value: int = None  # maximum value for unsigned types

    value: Numeric

    def __init__(self, value):
        self.value = value

    @property
    @abc.abstractmethod
    def _format(self) -> str:
        """Format for the struct.Struct instance."""
        pass

    @property
    def size(self) -> int:
        return self._struct.size

    @classmethod
    def unpack_from(cls, buffer: bytes, offset: Optional[int] = 0) -> Numeric:
        """Returns an unpacked value from raw bytes."""
        return cls._struct.unpack_from(buffer, offset)[0]

    @classmethod
    def from_buffer(cls, buffer: bytes, offset: Optional[int] = 0):
        """Returns the currently data type class instance."""
        return cls(cls.unpack_from(buffer, offset))

    def pack(self) -> bytes:
        """Returns a bytes object contains a packed value."""
        if self._format.isupper() and self.value < 0:  # unsigned < 0
            return self._struct.pack(self._max_value)
        return self._struct.pack(self.value)


class Boolean(NumericBase, int, metaclass=_DataTypeMeta):
    """Wraps a Boolean data type."""
    _format = '?'


class Char(NumericBase, bytes, metaclass=_DataTypeMeta):
    """Wraps a Char data type."""
    _format = 'c'


class Byte(NumericBase, int, metaclass=_DataTypeMeta):
    """Wraps a ShortInt data type."""
    _format = 'b'


class UByte(NumericBase, int, metaclass=_DataTypeMeta):
    """Wraps an Byte data type."""
    _format = 'B'


class Short(NumericBase, int, metaclass=_DataTypeMeta):
    """Wraps a SmallInt data type."""
    _format = 'h'


class UShort(NumericBase, int, metaclass=_DataTypeMeta):
    """Wraps a Dword data type."""
    _format = 'H'


class Int(NumericBase, int, metaclass=_DataTypeMeta):
    """Wraps an Integer data type."""
    _format = 'i'


class UInt(NumericBase, int, metaclass=_DataTypeMeta):
    """Wraps a Cardinal data type."""
    _format = 'I'


class Float(NumericBase, float, metaclass=_DataTypeMeta):
    """Wraps a Single data type."""
    _format = 'f'


class Double(NumericBase, float, metaclass=_DataTypeMeta):
    """Wraps a Double data type."""
    _format = 'd'


class Long(NumericBase, float, metaclass=_DataTypeMeta):
    """Wraps a Int64 data type."""
    _format = 'q'


class ULong(NumericBase, float, metaclass=_DataTypeMeta):
    """Wraps a UInt64 data type."""
    _format = 'Q'


class String(str):
    """Wraps a String data type."""

    _len_struct = struct.Struct('I')  # for string len serialization

    @property
    def _format(self) -> str:
        return f'I{len(self) * UNICODE_CHAR_LENGTH}s'

    @property
    def value(self) -> str:
        return str(self)

    @property
    def size(self) -> int:
        return struct.calcsize(self._format)

    @classmethod
    def unpack_from(cls, buffer: bytes, offset: Optional[int] = 0) -> str:
        """Returns an unpacked string from a given raw data."""
        length, = cls._len_struct.unpack_from(buffer, offset)
        offset += cls._len_struct.size
        return str(buffer[offset:offset + length * UNICODE_CHAR_LENGTH], CODEC)

    @classmethod
    def from_buffer(cls, buffer: bytes, offset: Optional[int] = 0) -> str:
        """Returns a String instance from a given raw data."""
        return cls(cls.unpack_from(buffer, offset))

    def pack(self) -> bytes:
        """Returns a bytes object contains a packed string and it's length."""
        return struct.pack(self._format, len(self), self.encode(encoding=CODEC))


class Buffer(bytes):
    """Wraps a Buffer data type."""

    @property
    def _format(self):
        return f'{len(self)}c'

    @property
    def value(self):
        return bytes(self)

    @classmethod
    def unpack_from(cls, buffer: bytes, offset: Optional[int] = 0) -> bytes:
        """Returns a bytes object as is."""
        return bytes(buffer[offset:])

    @classmethod
    def from_buffer(cls, buffer: bytes, offset: Optional[int] = 0) -> 'Buffer':
        """Returns a Buffer instance."""
        return cls(buffer[offset:])

    def pack(self) -> bytes:
        """Returns the bytes object from the current instance."""
        return self.value


# aliases for export
_bool = Boolean
_char = Char
_byte = Byte
_ubyte = UByte
_short = Short
_ushort = UShort
_int = Int
_uint = UInt
_float = Float
_double = Double
_long = Long
_ulong = ULong
_str = String
_buffer = Buffer
