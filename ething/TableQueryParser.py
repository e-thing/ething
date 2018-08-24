# coding: utf-8

from .query import Query, mongodb_compiler


class TableQueryParser(Query):

    def __init__(self, **kwargs):
        super(TableQueryParser, self).__init__(mongodb_compiler, fields = {
            'id': 'string',
            'date': 'date'
        }, **kwargs)

