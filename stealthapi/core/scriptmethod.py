"""This module provides a base class for all script methods."""

__all__ = ['ScriptMethod']

from stealthapi.config import TIMER_RES
from stealthapi.core.connection_container import get_connection
from stealthapi.core.datatypes import AnyArgType
from stealthapi.core.packet import packet_cmd_struct, packet_id_struct, \
    packet_size_struct
from stealthapi.core.utils import get_event_loop, sleep

_AnyArgType = type[AnyArgType]
_AnyArgArray = list[_AnyArgType] | tuple[_AnyArgType]


class ScriptMethod:
    """A base class for all script functions.

    :Example:
        >>> # for AddToSystemJournal
        >>> from stealthapi.core.scriptmethod import ScriptMethod
        >>> from stealthapi.core.datatypes import *
        >>> _add_to_system_journal = ScriptMethod(10, [Str], None)
    """

    index: int
    restype: AnyArgType
    argtypes: _AnyArgArray

    def __init__(self, index: int,
                 argtypes: _AnyArgArray = None,
                 restype: _AnyArgType = None) -> None:
        self.index = index
        self.argtypes = argtypes
        self.restype = restype

    def __call__(self, *args: AnyArgType) -> AnyArgType:
        loop = get_event_loop()
        loop.run_until_complete(self._call(args))

    async def _call(self, args: tuple[AnyArgType]) -> AnyArgType:
        """
        Check pause, form packet, send it to Stealth, wait for response and
        return it.
        """
        # check pause script
        connection = await get_connection()
        while connection.pause:
            await sleep(TIMER_RES)

        # form packet
        data = bytes()

        # serialize arguments
        for t, v in zip(self.argtypes, args):
            data += t(v).pack()

        # make packet and send to Stealth
        request_id = connection.request_id if self.restype else 0
        packet = await self._form_packet(request_id, args)
        connection.send(packet)

        # wait for a result
        while self.restype is not None:
            try:
                resp = connection.methods_responses.pop(request_id)
                result = self.restype.unpack_from(resp)
                return result.value
            except KeyError:
                await sleep(TIMER_RES)

    async def _form_packet(self, req_id: int, args: tuple[AnyArgType]) -> bytes:
        # packet header
        index = packet_cmd_struct.pack(self.index)
        request_id = packet_id_struct.pack(req_id)

        # method arguments
        packed_args = bytes()
        for cls, value in zip(self.argtypes, args):
            packed_args += cls(value).pack()

        # form packet
        data = index + request_id + packed_args  # packet data (header + args)
        size = packet_size_struct.pack(len(data))  # packet size

        return size + data
