# coding: utf-8

from .null_context_manager import NullContextManager
import inspect
import sys


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


if sys.version_info >= (3, 0):
    def get_cls_methods(cls):
      return inspect.getmembers(cls, inspect.isfunction)
else:
    def get_cls_methods(cls):
      return [(n,m.__func__) for n,m in inspect.getmembers(cls, inspect.ismethod)]


class _Comparable:
    def __init__(self, obj, cls, *args):
        self.obj = obj
        self.cls = cls

    def __lt__(self, other):

        if isinstance(self.obj, self.cls):
            if isinstance(other.obj, self.cls):
                return self.obj < other.obj
            else:
                return False
        else:
            return True


def object_sort(iterable, key=None, reverse=False, cls=None):
    if key is None:
        key = lambda v: v

    if cls is None:
        for obj in iterable:
            val = key(obj)
            if val is not None:
                cls = type(val)
                break
        else:
            # no item found !
            return iterable

    return sorted(iterable, key=lambda r: _Comparable(key(r), cls), reverse=reverse)
