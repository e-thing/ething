# coding: utf-8


from .utils import type_normalize, type_equals
from future.utils import string_types


class Field(object):

    def __init__(self, name, accepted_type=None):
        self._name = name

        if accepted_type is None or accepted_type == '*':
            self._type = '*'
        elif isinstance(accepted_type, string_types):
            self._type = [type_normalize(accepted_type)]
        else:
            self._type = [type_normalize(t) for t in accepted_type]

    @property
    def typeStr(self):
        if self._type == '*':
            return '*'
        else:
            return ','.join(self._type)

    @property
    def name(self):
        return self._name

    def isType(self, t):

        if t == '*':
            return self._type == '*'

        if self._type == '*':
            return True

        for _t in self._type:
            if type_equals(_t, t):
                return True

        return False

    def __str__(self):
        return self.name
