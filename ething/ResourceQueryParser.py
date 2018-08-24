# coding: utf-8

from .query import Query, AttributeCompiler


class ResourceQueryCompiler(AttributeCompiler):

  def _cast_value_(self, field, value):
    if field == 'createdBy':
      return value.id
    return value


compiler = ResourceQueryCompiler()


class ResourceQueryParser(Query):

    def __init__(self, **kwargs):
        super(ResourceQueryParser, self).__init__(compiler, **kwargs)
