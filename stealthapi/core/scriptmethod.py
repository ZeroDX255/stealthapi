"""This module provides a base class for all script methods."""

__all__ = ['ScriptMethod']

import asyncio
import logging

from stealthapi.config import TIMER_RES
from stealthapi.core.connection_container import ConnectionsContainer
from stealthapi.core.datatypes import AnyArgType
from stealthapi.core.packet import packet_cmd_struct, packet_id_struct, \
    packet_size_struct
from stealthapi.core.utils import IS_WIN, get_event_loop
from stealthapi.core.winmm import set_timer_resolution

_AnyArgTypeType = type[AnyArgType]


class ScriptMethod:
    """TODO"""

    index: int
    restype: AnyArgType
    argtypes: list[_AnyArgTypeType] | tuple[_AnyArgTypeType]

    def __call__(self, *args: AnyArgType) -> AnyArgType:
        """TODO"""

        loop = get_event_loop()
        loop.run_until_complete(self._call(args))

    async def _call(self, args: tuple[AnyArgType]) -> AnyArgType:
        """TODO"""
        # TODO: check pause script

        # form packet
        data = bytes()

        # serialize arguments
        for t, v in zip(self.argtypes, args):
            data += t(v).pack()

        # make packet and send to Stealth
        connection = await ConnectionsContainer.get_connection()
        request_id = connection.request_id
        packet = await self._form_packet(request_id, args)
        connection.send(packet)

        # wait for a result
        while self.restype is not None:
            try:
                resp = connection.methods_responses.pop(request_id)
                result = self.restype.unpack_from(resp)
                return result.value
            except KeyError:
                if IS_WIN:
                    with set_timer_resolution():
                        await asyncio.sleep(TIMER_RES)
                else:
                    await asyncio.sleep(TIMER_RES)

    async def _form_packet(self, request_id: int,
                           args: tuple[AnyArgType]) -> bytes:
        """TODO"""
        # packet header
        index = packet_cmd_struct.pack(self.index)
        request_id = packet_id_struct.pack(request_id)

        # method arguments
        packed_args = bytes()
        for cls, value in zip(self.argtypes, args):
            packed_args += cls(value).pack()

        # form packet
        data = index + request_id + packed_args  # packet data (header + args)
        size = packet_size_struct.pack(len(data))  # packet size

        return size + data


_logger = logging.getLogger(ScriptMethod.__class__.__name__)
