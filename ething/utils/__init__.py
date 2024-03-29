# coding: utf-8

import collections
import inspect
import types
from builtins import object
from shortid import ShortId as ShortIdlib
import operator
from future.utils import string_types


id_re = '^[-_a-zA-Z0-9]{7}$'

length = 7

alphabet = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_-'

sid = ShortIdlib()


def generate_id():
    return sid.generate()[-length:]



class NullContextManager(object):
    def __enter__(self):
        return None

    def __exit__(self, *args):
        pass

    def __bool__(self):
        return False


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
                and isinstance(merge_dct[k], collections.abc.Mapping)):
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


# Taken from http://stackoverflow.com/a/10077069
def etree_to_dict(t):
    """Convert an ETree object to a dict."""
    # strip namespace
    tag_name = t.tag[t.tag.find("}")+1:]

    d = {
        tag_name: {} if t.attrib else None
    }
    children = list(t)
    if children:
        dd = collections.defaultdict(list)
        for dc in map(etree_to_dict, children):
            for k, v in dc.items():
                dd[k].append(v)
        d = {tag_name: {k: v[0] if len(v) == 1 else v for k, v in dd.items()}}
    dt = d[tag_name]
    if t.attrib:
        assert dt is not None
        dt.update(('@' + k, v) for k, v in t.attrib.items())
    if t.text:
        text = t.text.strip()
        if children or t.attrib:
            if text:
                assert dt is not None
                dt['#text'] = text
        else:
            d[tag_name] = text
    return d


# Taken from https://gist.github.com/samuraisam/901117/521ed1ff8937cb43d7fcdbc1a6f6d0ed2c723bae
def deep_eq(_v1, _v2):
    """
    Tests for deep equality between two python data structures recursing
    into sub-structures if necessary. Works with all python types including
    iterators and generators. This function was dreampt up to test API responses
    but could be used for anything. Be careful. With deeply nested structures
    you may blow the stack.
    """

    def _deep_dict_eq(d1, d2):
        k1 = sorted(d1.keys())
        k2 = sorted(d2.keys())
        if k1 != k2:  # keys should be exactly equal
            return False
        return sum(deep_eq(d1[k], d2[k]) for k in k1) == len(k1)

    def _deep_iter_eq(l1, l2):
        if len(l1) != len(l2):
            return False
        return sum(deep_eq(v1, v2) for v1, v2 in zip(l1, l2)) == len(l1)

    op = operator.eq
    c1, c2 = (_v1, _v2)

    # guard against strings because they are also iterable
    # and will consistently cause a RuntimeError (maximum recursion limit reached)
    if isinstance(_v1, string_types):
        pass
    else:
        if isinstance(_v1, collections.abc.Mapping):
            op = _deep_dict_eq
        else:
            try:
                c1, c2 = (list(iter(_v1)), list(iter(_v2)))
            except TypeError:
                c1, c2 = _v1, _v2
            else:
                op = _deep_iter_eq

    return op(c1, c2)