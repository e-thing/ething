# coding: utf-8

from .query import Query


class TableQueryParser(Query):

    def __init__(self, compiler, **kwargs):
        super(TableQueryParser, self).__init__(compiler, fields = {
            'id': 'string',
            'date': 'date'
        }, **kwargs)

