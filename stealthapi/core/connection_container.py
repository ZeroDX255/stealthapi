"""

"""


__all__ = ['ConnectionsContainer']

import threading
import types

from stealthapi.config import HOST
from stealthapi.core.protocol import StealthConnection as Protocol
from stealthapi.core.utils import get_connection_port, get_event_loop


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

    @classmethod
    async def get_connection(cls) -> Protocol:
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