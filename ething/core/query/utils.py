# coding: utf-8
import collections


class TypeError(Exception):
    pass


types = collections.OrderedDict()

types['boolean'] = ('boolean', 'bool', 'logical')
types['integer'] = ('integer', 'int')
types['double'] = ('double', 'float')
types['string'] = ('string', 'str', 'unicode')
types['array'] = ('array', 'list')
types['object'] = ('object', 'dict')
types['null'] = ('null', 'none', 'nonetype')
types['number'] = ('number',) + types['integer'] + types['double']
types['date'] = ('date',)
types['regex'] = ('regex', 'SRE_Pattern')


def type_normalize(a):
    a = a.lower()

    for t in types:
        if a in types[t]:
            return t

    raise TypeError('unknown type "%s"' % a)


def type_equals(a, b):

    for a_synonym in types.get(type_normalize(a), ()):
        for b_synonym in types.get(type_normalize(b), ()):
            if a_synonym == b_synonym:
                return True

    return False
