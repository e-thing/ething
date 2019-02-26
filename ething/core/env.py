# coding: utf-8

import os
import tempfile


HOME_DIR = os.path.expanduser('~')
USER_DIR = os.path.join(HOME_DIR, '.ething')
PID_FILE = os.path.join(tempfile.gettempdir(), "ething.pid")
LOG_FILE = os.path.abspath(os.path.join(USER_DIR, 'ething.log'))
