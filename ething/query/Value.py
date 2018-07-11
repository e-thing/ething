# coding: utf-8
from future.utils import string_types, integer_types


#from dateutil.parser import parse
from dateparser import parse
import datetime
from .InvalidQueryException import InvalidQueryException
from .utils import type_normalize, type_equals


class Value(object):

    def __init__(self, parser, value=None):
        self.__parser = parser
        self.__value = value

    @property
    def type(self):
        return type_normalize(type(self.__value).__name__)

    # check if the value has the given type
    def isType(self, type):

        if type == 'date':
            return self.type == 'string' and self.isDate()

        return type_equals(self.type, type)

    def getValue(self):
        return self.__value

    def isDate(self):
        return bool(self.getDate())

    def getDate(self):
        if not hasattr(self, '__date'):
            self.__date = None
            try:
                tz = self.__parser.tz or 'UTC'
                d = parse(self.__value, languages=['en'], settings={'TIMEZONE': tz, 'TO_TIMEZONE': 'UTC'})
                if isinstance(d, datetime.datetime):
                    self.__date = d
            except:
                pass

        return self.__date

    def __str__(self):
        return str(self.__value)
