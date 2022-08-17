"""
This module provides tools for handling events.
"""

__all__ = []

from typing import Callable

from stealthapi.core.commands import SET_EVENT, UNSET_EVENT
from stealthapi.core.scriptmethod import ScriptMethod

_set_event = ScriptMethod(SET_EVENT)
_unset_event = ScriptMethod(UNSET_EVENT)


class _Event:
    _index: int
    handler: Callable

    def set(self):
        pass
        # _set_event(self._index)

    def unset(self):
        pass
        # _unset_event(self._index)


class ItemInfoEvent(_Event):
    _index = 0
    handler: Callable


class ItemDeleted(_Event):
    _index = 1


class Speech(_Event):
    _index = 2
