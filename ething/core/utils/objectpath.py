# coding: utf-8
from future.utils import string_types, integer_types
import objectpath
from objectpath.utils import timeutils
from .date import parse, utcfromtimestamp
from ..type import String


def generate_filter(expr, converter=None):
    if converter is None:
        converter = lambda x:x

    def _filter(obj):
        try:
            tree = objectpath.Tree(converter(obj))
            return bool(tree.execute(expr))
        except:
            return False
    return _filter


def evaluate(expr, data):
    return generate_filter(expr)(data)


dateTime_orig = timeutils.dateTime


def patch_dateTime(core):

    def patched_dateTime(arg):

        if isinstance(arg, string_types):
            return parse(arg, core.local_tz)
        elif isinstance(arg, integer_types):
            # timestamp
            return utcfromtimestamp(arg)

        return dateTime_orig(arg)

    timeutils.dateTime = patched_dateTime


def patch_all(core, **kwargs):

    dateTime = kwargs.get('dateTime', True)

    if dateTime:
        patch_dateTime(core)


class ObjectPathExp(String):
    def __init__(self, **attributes):
        super(ObjectPathExp, self).__init__(allow_empty=False, **attributes)

    def toSchema(self, context = None):
        s = super(ObjectPathExp, self).toSchema(context)
        s['$component'] = 'OpenPathExpression'
        return s
