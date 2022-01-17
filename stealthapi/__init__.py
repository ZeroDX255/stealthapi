"""An alternate API for Stealth UO client."""

__author__ = 'Igor Timofeev <zerodx@mail.ru>'

import logging

from stealthapi import config, events, sysjournal
from stealthapi.misc import *

__all__ = ['config', 'events', 'sysjournal'] + misc.__all__

if config.DEBUG:
    logging.basicConfig(level=logging.DEBUG)
