"""An alternate API for Stealth UO client."""

__author__ = 'Igor Timofeev <zerodx@mail.ru>'

import logging

from . import config

__all__ = ['config']

if config.DEBUG:
    logging.basicConfig(level=logging.DEBUG)
