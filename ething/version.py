# coding: utf-8

try:
    import pkg_resources
except ImportError:
    pass


try:
    __version__ = pkg_resources.require('ething')[0].version
except Exception:
    __version__ = 'unknown'
