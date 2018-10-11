# coding: utf-8

import json
import datetime
import sys
from future.utils import iteritems, binary_type


def dict_recursive_update(a, *more):
    for b in more:
        for k, v in iteritems(b):
            if isinstance(v, dict) and k in a and isinstance(a[k], dict):
                a[k] = dict_recursive_update(a.get(k, {}), v)
            else:
                a[k] = v
    return a


def serialize(obj):
    """JSON serializer for objects not serializable by default json code"""
    if hasattr(obj, 'toJson'):
        return obj.toJson()
    if isinstance(obj, datetime.datetime):
        return obj.isoformat()
    if isinstance(obj, binary_type):
        return obj.decode('utf8')
    return obj.__dict__


def filter_obj(obj, fields):
    cpy = {}
    for f in fields:
        if f in obj:
            cpy[f] = obj[f]
    return cpy


def toJson(obj, fields=None, **kwargs):

    # filter by keys
    if fields is not None:
        if isinstance(obj, dict):
            obj = filter_obj(obj, fields)
        elif isinstance(obj, list):
            obj = [filter_obj(o, fields) for o in obj]

    return json.dumps(obj, default=serialize, **kwargs)



# cf. https://stackoverflow.com/questions/6062576/adding-information-to-an-exception/6062799
if sys.version_info.major < 3:  # Python 2?
    # Using exec avoids a SyntaxError in Python 3.
    exec("""def reraise(exc_type, exc_value, exc_traceback=None):
                raise exc_type, exc_value, exc_traceback""")
else:
    def reraise(exc_type, exc_value, exc_traceback=None):
        if exc_value is None:
            exc_value = exc_type()
        if exc_value.__traceback__ is not exc_traceback:
            raise exc_value.with_traceback(exc_traceback)
        raise exc_value


def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        pass

    try:
        import unicodedata
        unicodedata.numeric(s)
        return True
    except (TypeError, ValueError):
        pass

    return False


def topological_sort(source):
    """perform topo sort on elements.

    :arg source: list of ``(name, [list of dependancies])`` pairs
    :returns: list of names, with dependancies listed first
    """
    pending = [(name, set(deps)) for name, deps in source] # copy deps so we can modify set in-place
    emitted = []
    while pending:
        next_pending = []
        next_emitted = []
        for entry in pending:
            name, deps = entry
            deps.difference_update(emitted) # remove deps we emitted last pass
            if deps: # still has deps? recheck during next pass
                next_pending.append(entry)
            else: # no more deps? time to emit
                yield name
                emitted.append(name) # <-- not required, but helps preserve original ordering
                next_emitted.append(name) # remember what we emitted for difference_update() in next pass
        if not next_emitted: # all entries have unmet deps, one of two things is wrong...
            raise ValueError("cyclic or missing dependancy detected: %r" % (next_pending,))
        pending = next_pending
        emitted = next_emitted
