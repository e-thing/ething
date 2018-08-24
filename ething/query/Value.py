# coding: utf-8

#from dateutil.parser import parse
from dateparser import parse
import datetime
from .utils import type_normalize, type_equals


class Value(object):
    def __init__(self, parser, value=None, value_type = None):
        self.__parser = parser
        self.__value = value

        if value_type is None:
          value_type = type(self.__value).__name__
        
        self.__type = type_normalize(value_type)

    @property
    def type(self):
        return self.__type

    # check if the value has the given type
    def isType(self, value_type):

        if value_type == 'date':
            return self.type == 'string' and self.isDate()

        return type_equals(self.type, value_type)

    def getValue(self):
        return self.__value

    def isDate(self):
        return bool(self.getDate())

    def getDate(self):
        if not hasattr(self, '__date'):
            self.__date = None
            try:
                tz = self.__parser.tz
                d = parse(
                    self.__value,
                    languages=['en'],
                    settings={
                        'TIMEZONE': tz,
                        'TO_TIMEZONE': 'UTC'
                    })
                if isinstance(d, datetime.datetime):
                    self.__date = d
            except:
                pass

        return self.__date

    def __str__(self):
        return str(self.__value)
