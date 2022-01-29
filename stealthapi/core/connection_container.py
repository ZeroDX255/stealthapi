"""This module provides stuff to store StealthConnection instances."""

__all__ = ['get_connection']

import threading
import types

from stealthapi.config import HOST
from stealthapi.core.protocol import StealthConnection
from stealthapi.core.utils import get_connection_port, get_event_loop

_lock = threading.Lock()
_connections: dict[int, StealthConnection] = {}


def _disconnect(thread_id: int) -> None:
    """Close connection with Stealth for the thread with the specified id."""
    with _lock:
        del _connections[thread_id]


def _join(self: threading.Thread, timeout: float | None = None) -> None:
    """This method should be injected to every new thread."""
    _disconnect(self.ident)
    self.__class__.join(self, timeout)


async def _create_connection() -> StealthConnection:
    """Create a new connection with Stealth and return it."""
    port = await get_connection_port()
    loop = get_event_loop()
    _, protocol = await loop.create_connection(StealthConnection, HOST, port)
    # noinspection PyTypeChecker
    return protocol


async def get_connection() -> StealthConnection:
    """
    Get a connections with Stealth for the current thread. Create a new one,
    if there is no StealthConnection instance for the current thread.
    """
    thread = threading.current_thread()
    with _lock:
        if thread.ident not in _connections:
            protocol = await _create_connection()
            _connections[thread.ident] = protocol

            # replace the join method for the current thread
            thread.join = types.MethodType(_join, thread)

        return _connections[thread.ident]
