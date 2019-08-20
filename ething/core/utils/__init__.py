# coding: utf-8

from .null_context_manager import NullContextManager
import collections
import inspect
import types


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


def dict_merge(dct, merge_dct):
    """ Recursive dict merge. Inspired by :meth:``dict.update()``, instead of
    updating only top-level keys, dict_merge recurses down into dicts nested
    to an arbitrary depth, updating keys. The ``merge_dct`` is merged into
    ``dct``.
    :param dct: dict onto which the merge is executed
    :param merge_dct: dct merged into dct
    """
    for k in merge_dct:
        if (k in dct and isinstance(dct[k], dict)
                and isinstance(merge_dct[k], collections.Mapping)):
            dict_merge(dct[k], merge_dct[k])
        else:
            dct[k] = merge_dct[k]


# from inspect
def getmembers(obj, predicate=None):
    """Return all members of an object as (name, value) pairs sorted by name.
    Optionally, only return members that satisfy a given predicate."""
    if inspect.isclass(obj):
        cls = obj
    else:
        cls = type(obj)

    mro = (obj,) + cls.__mro__

    results = []
    processed = set()
    names = dir(obj)
    # :dd any DynamicClassAttributes to the list of names if object is a class;
    # this may result in duplicate entries if, for example, a virtual
    # attribute with the same name as a DynamicClassAttribute exists
    try:
        for base in obj.__bases__:
            for k, v in base.__dict__.items():
                if isinstance(v, types.DynamicClassAttribute):
                    names.append(k)
    except AttributeError:
        pass
    for key in names:
        # directly looking in the __dict__.
        for base in mro:
            if key in base.__dict__:
                value = base.__dict__[key]
                break
        else:
            # could be a (currently) missing slot member, or a buggy
            # __dir__; discard and move on
            continue
        if not predicate or predicate(value):
            results.append((key, value))
        processed.add(key)
    results.sort(key=lambda pair: pair[0])
    return results


def filter_obj(obj, fields):
    cpy = {}
    for f in fields:
        if f in obj:
            cpy[f] = obj[f]
    return cpy

