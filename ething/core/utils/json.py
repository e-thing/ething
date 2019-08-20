# coding: utf-8

import json as _json
import datetime
from future.utils import binary_type


__all__ = [
    'dumps',
]


def serialize(obj):
    """JSON serializer for objects not serializable by default json code"""
    if hasattr(obj, '__json__'):
        return obj.__json__()
    if isinstance(obj, datetime.datetime):
        return obj.isoformat()
    if isinstance(obj, binary_type):
        return obj.decode('utf8')
    if hasattr(obj, '__dict__'):
        return obj.__dict__
    return type(obj).__name__


def dumps(obj, **kwargs):
    return _json.dumps(obj, default=serialize, **kwargs)
