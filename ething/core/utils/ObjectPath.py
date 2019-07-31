# coding: utf-8
from future.utils import string_types, integer_types
import objectpath
from .date import parse, utcfromtimestamp
from ..type import String



class MTree(objectpath.Tree):

    def __init__(self, expr, cfg=None):
        super(MTree, self).__init__(None, cfg)
        self.c_expr = self.optimize(objectpath.parse(expr, self.D))

    def compile(self, expr):
        return self.c_expr

    def execute(self, obj):
        self.data = obj
        return super(MTree, self).execute('')

    def optimize(self, c_expr):
        # try to optimize static op

        def check(node):
            if isinstance(node, tuple):
                node_op = node[0]
                if node_op == 'fn' and node[1] == 'dateTime' and len(node)==3 and isinstance(node[2], string_types):
                    return objectpath.timeutils.dateTime(node[2:])

                node = tuple([check(n) for n in node])

            return node

        c_expr = check(c_expr)

        return c_expr



def generate_filter(expr, converter=None):
    if converter is None:
        converter = lambda x:x

    tree = MTree(expr)

    def _filter(obj):
        try:
            res = tree.execute(converter(obj))
            return res
        except:
            return None
    return _filter


def evaluate(expr, data):
    return generate_filter(expr)(data)


dateTime_orig = objectpath.timeutils.dateTime


def patch_dateTime(core):

    def patched_dateTime(arg):
        # must return an offset aware datetime
        if isinstance(arg[0], string_types):
            dt = parse(arg[0], core.config.timezone)
        elif isinstance(arg[0], integer_types):
            # timestamp
            dt = utcfromtimestamp(arg[0])
        else:
            dt = dateTime_orig(arg)

        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=core.local_tz)

        return dt

    objectpath.timeutils.dateTime = patched_dateTime


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
