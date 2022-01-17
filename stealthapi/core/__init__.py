"""
This package provides all the stuff needed to establish a connection with
Stealth and exchange data through it.
"""

import logging

from stealthapi.config import DEBUG

if DEBUG:
    logging.basicConfig(level=logging.DEBUG)
