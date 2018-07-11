# coding: utf-8

from .query.Parser import Parser
from .query.Field import Field
import re
import sys


def getDefaultFields():

    fieldId = Field('_id')

    def idCompil(op, value):
        # shortcut
        return fieldId.compil(op, value)

    return [
        Field('id', 'string', idCompil),
        Field('date', 'date')
    ]


class TableQueryParser(Parser):

    fields = getDefaultFields()

    def __init__(self, **kwargs):

        super(TableQueryParser, self).__init__(fields = TableQueryParser.fields, **kwargs)

        self.setFieldFallback(self.fallback)

    def fallback(self, field):
        return Field(field)

    @staticmethod
    def check(expr):
        message = ''
        ok = True
        try:
            parser = TableQueryParser()
            parser.parse(expr)
        except:
            ok = False
            message = sys.exc_info()[1]

        return ok, message
