# coding: utf-8

from .pingable import pingable

from .nodejs import *

from .null_context_manager import NullContextManager

_info = None


def get_info(core):
    global _info

    if _info is None:
        import platform
        import sys

        _info = {
            'VERSION': core.version,
            'python': {
                'version': platform.python_version(),
                'type': platform.python_implementation(),
                'executable': sys.executable
            },
            'platform': {
                'name': "%s %s" % (sys.platform, platform.platform()),
                'version': platform.version()
            },
            'nodejs': {
                'version': (is_nodejs_installed(core) or "not found")
            },
            'mongodb': {
                'version': core.mongoClient.server_info().get('version') if hasattr(core, 'mongoClient') else None
            }
        }

    return _info


def print_info(core, printer):
    info = get_info(core)

    printer("ETHING    : version=%s" % info.get('VERSION'))

    python_info = info.get('python', {})
    printer("PYTHON    : version=%s type=%s" %
            (python_info.get('version'), python_info.get('type')))
    printer("PYTHON_EXE: %s" % (python_info.get('executable')))

    platform_info = info.get('platform', {})
    printer("PLATFORM  : %s" % (platform_info.get('name')))
    printer("SYSTEM    : %s" % (platform_info.get('version')))

    mongodb_info = info.get('mongodb', {})
    printer("MONGODB   : %s" % (mongodb_info.get('version')))

    nodejs_info = info.get('nodejs', {})
    printer("NODE.JS   : %s" % (nodejs_info.get('version')))
