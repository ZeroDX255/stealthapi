"""This module provides some common tools and tools without category."""

__all__ = ['wait']

import asyncio

from stealthapi.core.utils import get_event_loop


def wait(delay: int) -> None:
    """Delay script execution for a given number of milliseconds.

    :Example:
        >>> from stealthapi import wait
        >>> wait(1000)  # wait 1 second

    :param delay:
    :return:
    """
    loop = get_event_loop()
    loop.run_until_complete(asyncio.sleep(delay / 1000))


