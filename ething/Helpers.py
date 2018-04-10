# coding: utf-8

import json
import datetime
import sys
from future.utils import iteritems


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
    return obj.__dict__


def toJson(obj, **kwargs):
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



