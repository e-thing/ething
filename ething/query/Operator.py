# coding: utf-8
from future.utils import string_types
from .utils import type_normalize
from .InvalidQueryException import InvalidQueryException


class Operator(object):

    def __init__(self, name, accept_field='*', accept_value='*'):

        self.name = name

        if isinstance(accept_field, string_types) and accept_field != '*':
          accept_field = [accept_field]
        
        if isinstance(accept_field, list):
          accept_field = [type_normalize(t) for t in accept_field]
        
        if isinstance(accept_value, string_types) and accept_value != '*':
          accept_value = [accept_value]
        
        if isinstance(accept_value, list):
          accept_value = [type_normalize(t) for t in accept_value]

        self.__acceptField = accept_field
        self.__acceptValue = accept_value

    def accept(self, field, value):

        if not self.acceptField(field):
            raise InvalidQueryException(
                "not compatible with the field '%s'[type=%s]" % (self, field, field.typeStr))

        if not self.acceptValue(value):
            raise InvalidQueryException(
                "not compatible with value of type %s" % type_normalize(type(value.getValue()).__name__))

        return True

    def acceptField(self, field):
        if self.__acceptField == '*':
            return True

        for t in self.__acceptField:
            if field.isType(t):
                return True

        return False

    def acceptValue(self, value):

        if self.__acceptValue == '*':
            return True

        if not self.hasValue():
            return value is None

        for t in self.__acceptValue:
            if value.isType(t):
                return True

        return False

    def hasValue(self):
        return self.__acceptValue is not False
    
    def cast_value(self, value):
      return value.getValue()

    def __str__(self):
        return self.name



# default operators

class DateOperator(Operator):

  def cast_value(self, value):

        if value.isType('date'):
            v = value.getDate()
        else:
            v = value.getValue()
        
        return v


class EqualOperator(DateOperator):

    def __init__(self):
        super(EqualOperator, self).__init__('eq')


class NotEqualOperator(DateOperator):

    def __init__(self):
        super(NotEqualOperator, self).__init__('ne')


class ExistOperator(Operator):

    def __init__(self):
        super(ExistOperator, self).__init__('exists', accept_value = False)


class IsOperator(Operator):

    def __init__(self):
        super(IsOperator, self).__init__('is', accept_value = 'string')

    def cast_value(self, value):
        return type_normalize(value.getValue())


class LowerOperator(DateOperator):

    def __init__(self):
        super(LowerOperator, self).__init__(
            'lt', accept_field = ['number', 'date'], accept_value = ['number', 'date'])


class GreaterOperator(DateOperator):

    def __init__(self):
        super(GreaterOperator, self).__init__(
            'gt', accept_field = ['number', 'date'], accept_value = ['number', 'date'])


class LowerOrEqualOperator(Operator):

    def __init__(self):
        super(LowerOrEqualOperator, self).__init__(
            'le', accept_field = 'number', accept_value = 'number')


class GreaterOrEqualOperator(Operator):

    def __init__(self):
        super(GreaterOrEqualOperator, self).__init__(
            'ge', accept_field = 'number', accept_value = 'number')


class HasOperator(Operator):

    def __init__(self):
        super(HasOperator, self).__init__(
            'has', accept_field = ['array', 'object'], accept_value = '*')


class MatchOperator(Operator):

    def __init__(self):
        super(MatchOperator, self).__init__(
            'match', accept_field = 'string', accept_value = 'regex')
