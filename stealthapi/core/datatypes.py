"""This module provides basic data types."""

__all__ = ['Bool', 'Char', 'Byte', 'UByte', 'Short', 'UShort', 'Int', 'UInt',
           'Float', 'Double', 'Long', 'ULong', 'Str', 'Buffer', 'AnyArgType']

import struct

from stealthapi.config import ENDIAN, STEALTH_CODEC

_unicode_length = len('c'.encode(STEALTH_CODEC))

NumberType = int | float


class _DataTypeMeta(type):
    """Metaclass creates a struct.Struct instance for data type classes."""

    def __new__(mcs, *args, **kwargs):
        cls = super().__new__(mcs, *args, **kwargs)
        if '_fmt' in args[-1]:
            cls._struct = struct.Struct(ENDIAN + args[-1]['_fmt'])
        return cls


class _NumberBase:
    """Base class for all numeric data types."""

    _fmt: str
    _struct: struct.Struct
    _value: NumberType

    def __init__(self, value: NumberType) -> None:
        self._value = value

    @property
    def value(self) -> NumberType:
        return self._value

    @property
    def size(self):
        return self._struct.size

    @classmethod
    def unpack_from(cls, buffer: bytes, offset: int = 0) -> '_NumberBase':
        value, = cls._struct.unpack_from(buffer, offset)
        return cls(value)

    def pack(self) -> bytes:
        if self._fmt.isupper() and self._value < 0:  # unsigned < 0
            # set to max value
            return self._struct.pack(2 ** (self._struct.size * 8) - 1)
        return self._struct.pack(self._value)


class Bool(_NumberBase, metaclass=_DataTypeMeta):
    _fmt = '?'
    _value: bool

    @property
    def value(self) -> bool:
        return self._value


class Char(_NumberBase, metaclass=_DataTypeMeta):
    _fmt = 'c'


class Byte(_NumberBase, metaclass=_DataTypeMeta):
    _fmt = 'b'


class UByte(_NumberBase, metaclass=_DataTypeMeta):
    _fmt = 'B'


class Short(_NumberBase, metaclass=_DataTypeMeta):
    _fmt = 'h'


class UShort(_NumberBase, metaclass=_DataTypeMeta):
    _fmt = 'H'


class Int(_NumberBase, metaclass=_DataTypeMeta):
    _fmt = 'i'


class UInt(_NumberBase, metaclass=_DataTypeMeta):
    _fmt = 'I'


class Float(_NumberBase, metaclass=_DataTypeMeta):
    _fmt = 'f'


class Double(_NumberBase, metaclass=_DataTypeMeta):
    _fmt = 'd'


class Long(_NumberBase, metaclass=_DataTypeMeta):
    _fmt = 'q'


class ULong(_NumberBase, metaclass=_DataTypeMeta):
    _fmt = 'Q'


class Str:
    _size_struct = struct.Struct(ENDIAN + 'I')  # uint for string size
    _value: str

    def __init__(self, value: str) -> None:
        self._value = value

    @property
    def _fmt(self) -> str:
        chars_len = len(self._value) * _unicode_length
        return self._size_struct.format + f'{chars_len}s'

    @property
    def value(self) -> str:
        return self._value

    @classmethod
    def unpack_from(cls, buffer: bytes, offset: int = 0) -> 'Str':
        size, = cls._size_struct.unpack_from(buffer, offset)
        offset += cls._size_struct.size
        return cls(buffer[offset: offset + size].decode(STEALTH_CODEC))

    def pack(self) -> bytes:
        data = self._value.encode(STEALTH_CODEC)
        return struct.pack(self._fmt, len(self._value) * _unicode_length, data)


class Buffer(_NumberBase):
    _value: bytes

    @property
    def _fmt(self) -> str:
        return f'{len(self._value)}s'

    @property
    def size(self) -> int:
        return struct.calcsize(self._fmt)

    @classmethod
    def unpack_from(cls, buffer: bytes, offset: int = 0) -> 'Buffer':
        return cls(buffer[offset:])

    def pack(self) -> bytes:
        return bytes(self._value)


AnyArgType = Bool | Char | Byte | UByte | Short | UShort | Int | UInt | Float \
             | Double | Long | ULong | Str | Buffer
