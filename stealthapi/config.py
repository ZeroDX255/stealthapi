"""
This module loads the configuration file and provides all of its settings. If
the file does not exist - the module will create a new one and fill it with the
default values.

All configuration values provides as names of this module. To add a new one,
put it in the __all__ list.

:Example:
>>> from stealthapi.config import DEBUG
>>> print(DEBUG)
False
"""

__all__ = ['HOST', 'PORT', 'ENDIAN', 'STEALTH_CODEC', 'TIMER_RES', 'DEBUG']

import configparser
import os
import sys
from typing import Literal

_CONFIG_FILE_NAME = 'stealthapi.cfg'
_SECTION_NAME = 'GENERAL'

# default values
HOST = 'localhost'  # stealth host
PORT = 47602  # port provider server port

ENDIAN: Literal['<', '>', '='] = '<'  # "<" for little endian, ">" for big
STEALTH_CODEC = 'UTF-16LE'  # unicode codec used by Stealth

TIMER_RES = .005  # timer resolution (delay in loops, milliseconds)

DEBUG = False  # set to True if you want to see debug messages


def load_from_file(path: str) -> None:
    """Open a file with the given path and load settings from there.

    If any configuration value is not presented in the file - add it.

    :param path: the filepath of the existed configuration file
    :raises TypeError: if the path argument is not string
    :raises ValueError: if the path argument is empty
    :raises FileNotFoundError: if file with the provided path not exists
    """
    # check arg is correct
    if type(path) is not str:
        raise TypeError('The path argument must be string.')
    if not path:
        raise ValueError('The path argument must be not empty.')
    if not os.path.exists(path):
        raise FileNotFoundError('File with the given path not exists.')

    config = configparser.ConfigParser()
    config.read(path)

    # rewrite config values in the current module
    save = False
    module = sys.modules[__name__]
    for key in __all__:
        if key in config[_SECTION_NAME]:
            # try to convert to needed type before setting, if there will be an
            # error - use the default value
            default = getattr(module, key, '')
            type_ = type(default)
            raw = config[_SECTION_NAME][key]
            try:
                value = raw == 'True' if type_ is bool else type_(raw)
                setattr(module, key, value)
            except ValueError:
                # warn if there was an error while converting value
                import logging
                logging.warning(f'Can not apply the "{key}={raw}" parameter '
                                f'from the configuration file. The default '
                                f'value "{default}" will be used.')

        else:
            save = True
            config[_SECTION_NAME][key] = str(getattr(module, key))

    if save:
        with open(path, 'w') as file:
            config.write(file)


def create_config_file(path: str) -> None:
    """Create a new file with the given path and save the config values into it.

    :param path: the filepath of a new configuration file
    :raises TypeError: if the path argument is not string
    :raises ValueError: if the path argument is empty
    :raises FileExistsError: if file with the provided path already exists
    """
    # check arg is correct
    if type(path) is not str:
        raise TypeError('The path argument must be string.')
    if not path:
        raise ValueError('The path argument must be not empty.')
    if os.path.exists(path):
        raise FileExistsError(f'File "{path}" already exists.')

    config = configparser.ConfigParser()
    config.add_section(_SECTION_NAME)

    module = sys.modules[__name__]
    for key in __all__:
        config[_SECTION_NAME][key] = str(getattr(module, key))

    with open(path, 'w') as file:
        config.write(file)


# load or create a config on module initialization
default_path = os.path.join(os.path.dirname(__file__), _CONFIG_FILE_NAME)
try:
    load_from_file(default_path)
except FileNotFoundError:
    create_config_file(default_path)
