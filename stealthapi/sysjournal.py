"""
This module provides functions to work with the Stealth system journal.

add(*args: any, sep: str = ' ', end: str = '', **kwargs: any) -> None
clear() -> None

:Example:
>>> from stealthapi import sysjournal
>>> sysjournal.add('coordinates:', x=10, y=15, sep=' ')
"""

__all__ = ['add', 'clear']

from stealthapi.core.commands import SC_ADD_TO_SYSTEM_JOURNAL, \
    SC_CLEAR_SYSTEM_JOURNAL
from stealthapi.core.scriptmethod import ScriptMethod

_add_to_system_journal = ScriptMethod(SC_ADD_TO_SYSTEM_JOURNAL)
_clear_system_journal = ScriptMethod(SC_CLEAR_SYSTEM_JOURNAL)


def add(*args: any, sep: str = ', ', **kwargs: any) -> None:
    """Print the given data to the Stealth system journal.

    :Example:
    >>> from stealthapi import sysjournal
    >>> sysjournal.add('coordinates:', x=10, y=15, sep=' ')

    :param args: arguments will be converted to string with str()-function
    :param sep: separator will be placed between arguments
    :param kwargs: keyword arguments will be converted to `key=val` string
    :return:
    """
    args_ = sep.join((str(arg) for arg in args))
    kwargs_ = sep.join((f'{key}={value}' for key, value in kwargs.items()))
    _add_to_system_journal(args_ + (sep if args_ and kwargs_ else '') + kwargs_)


def clear() -> None:
    """ Clear the Stealth system journal.

    :Example:
    >>> from stealthapi import sysjournal
    >>> sysjournal.clear()
    """
    _clear_system_journal()
