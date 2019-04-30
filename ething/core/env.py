# coding: utf-8

import os
import tempfile


HOME_DIR = os.path.expanduser('~')
USER_DIR = os.path.join(HOME_DIR, '.ething')
LOG_FILE = os.path.abspath(os.path.join(USER_DIR, 'ething.log'))
