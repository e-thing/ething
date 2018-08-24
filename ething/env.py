# coding: utf-8

import os
import tempfile


HOME_DIR = os.path.expanduser('~')
USER_DIR = os.path.join(HOME_DIR, '.ething')
CONFIG_FILE = os.path.join(USER_DIR, 'config.json')
PID_FILE = os.path.join(tempfile.gettempdir(), "ething.pid")
LOG_DIR = os.getenv('APPDATA') if os.name == 'nt' else '/var/log'
LOG_FILE = os.path.abspath(os.path.join(LOG_DIR, 'ething.log'))