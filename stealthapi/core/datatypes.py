"""This module provides basic data types."""

__all__ = ['DataTypeMeta', 'DataTypeBase', 'Bool', 'Char', 'Byte', 'UByte',
           'Short', 'UShort', 'Int', 'UInt', 'Float', 'Double', 'Long', 'ULong',
           'Str', 'Buffer', 'DateTime', 'AnyArgType']

import abc
import datetime
import struct

from stealthapi.config import ENDIAN, STEALTH_CODEC

_unicode_length = len('c'.encode(STEALTH_CODEC))

NumberType = int | float


class DataTypeMeta(abc.ABCMeta):
    """Metaclass creates a struct.Struct instance for data type classes."""

    def __new__(mcs, *args, **kwargs):
        cls = super().__new__(mcs, *args, **kwargs)
        if '_fmt' in args[-1]:
            cls._struct = struct.Struct(ENDIAN + args[-1]['_fmt'])
        return cls


class DataTypeBase(abc.ABC):
    """
    A base class for all data type classes. It provides an interface used by
    other tools. If you want to add a new data type, make sure it will match
    interface of this class.
    """

    _fmt: str
    _struct: struct.Struct
    _value: object

    def __init__(self, value: object) -> None:
        self._value = value

    @property
    @abc.abstractmethod
    def value(self) -> object:
        """
        User doesn't want to find a UInt instance where an integer instance
        was expected. So this getter should return python data type for all
        primitives.
        """
        raise NotImplemented

    @property
    @abc.abstractmethod
    def size(self) -> int:
        """Size in bytes of the current instance when it is packed."""
        raise NotImplemented

    @classmethod
    @abc.abstractmethod
    def unpack_from(cls, buffer: bytes, offset: int = 0) -> object:
        """
        Return an instance of datatype unpacked from the given buffer with the
        given offset.
        """
        raise NotImplemented

    @abc.abstractmethod
    def pack(self) -> bytes:
        """Return a bytes object containing a value of the current instance."""
        raise NotImplemented


class _NumberBase(DataTypeBase, metaclass=DataTypeMeta):
    """Base class for all numeric data types."""

    _value: NumberType

    @property
    def value(self) -> NumberType:
        return self._value

    @property
    def size(self) -> int:
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


class Bool(_NumberBase):
    _fmt = '?'
    _value: bool

    @property
    def value(self) -> bool:
        return self._value


class Char(_NumberBase):
    _fmt = 'c'


class Byte(_NumberBase):
    _fmt = 'b'


class UByte(_NumberBase):
    _fmt = 'B'


class Short(_NumberBase):
    _fmt = 'h'


class UShort(_NumberBase):
    _fmt = 'H'


class Int(_NumberBase):
    _fmt = 'i'


class UInt(_NumberBase):
    _fmt = 'I'


class Float(_NumberBase):
    _fmt = 'f'


class Double(_NumberBase):
    _fmt = 'd'


class Long(_NumberBase):
    _fmt = 'q'


class ULong(_NumberBase):
    _fmt = 'Q'


class Str(DataTypeBase):
    _size_struct = struct.Struct(ENDIAN + 'I')  # uint for string size
    _value: str

    @property
    def _fmt(self) -> str:
        chars_len = len(self._value) * _unicode_length
        return self._size_struct.format + f'{chars_len}s'

    @property
    def size(self) -> int:
        return struct.calcsize(self._fmt)

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


class Buffer(DataTypeBase):
    _value: bytes

    @property
    def value(self) -> bytes:
        return self._value

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


class DateTime(DataTypeBase, metaclass=DataTypeMeta):
    _fmt = 'd'
    _value: datetime.datetime
    _delphi_epoch = datetime.datetime(1899, 12, 30)

    @property
    def value(self) -> datetime.datetime:
        return self._value

    @property
    def size(self) -> int:
        return self._struct.size

    @classmethod
    def unpack_from(cls, buffer: bytes, offset: int = 0) -> 'DateTime':
        value, = cls._struct.unpack_from(buffer, offset)
        return cls(cls._delphi_epoch + datetime.timedelta(days=value))

    def pack(self) -> bytes:
        delta = self._value - self._delphi_epoch
        seconds = delta.seconds + delta.microseconds / 1_000_000
        days = delta.days + seconds / 3600 / 24
        return self._struct.pack(days)


AnyArgType = Bool | Char | Byte | UByte | Short | UShort | Int | UInt | Float \
             | Double | Long | ULong | Str | Buffer | DateTime
