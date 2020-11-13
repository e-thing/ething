# coding: utf-8

import os
import configparser


HOME_DIR  = os.path.expanduser('~')
USER_DIR  = os.path.join(HOME_DIR, '.ething')
LOG_FILE  = os.path.abspath(os.path.join(USER_DIR, 'ething.log'))
CONF_FILE = os.path.abspath(os.path.join(USER_DIR, 'ething.cfg'))


_env = {}


def init_env ():
    global _env

    ini = configparser.ConfigParser()
    if os.path.isfile(CONF_FILE):
        ini.read(CONF_FILE)

    _env = {}

    # get from ini config file
    for section in ini:
        _env[section] = {}
        for key in ini[section]:
            _env[section][key] = ini[section][key]


def get_env ():
    global _env
    return _env


def get_options (section = 'core'):
    return get_env().get(section, {})


def get_option(section, name, default=None):
    return get_options(section).get(name, default)


def set_option(section, name, value):
    global _env
    if section not in _env:
        _env[section] = {}
    _env[section][name] = value
