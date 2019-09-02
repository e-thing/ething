# coding: utf-8

import os
import tempfile


HOME_DIR = os.path.expanduser('~')
USER_DIR = os.path.join(HOME_DIR, '.ething')
LOG_FILE = os.path.abspath(os.path.join(USER_DIR, 'ething.log'))


_ns = None


def _set_namespace(ns):
    global _ns
    _ns = ns


def get_option(name, default=None):
    global _ns

    # cli argument
    if _ns is not None:
        for arg_name in _ns.__dict__:
            if name.lower() == arg_name.lower():
                return getattr(_ns, arg_name)

    # env variables
    return os.environ.get('ETHING_%s' % name.upper(), default)
