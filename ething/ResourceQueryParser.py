# coding: utf-8

from .query.Parser import Parser
from .query.Field import Field
from .reg import *
import sys


def custom_fields(name, type, schema, default_field):
    if name == 'id':
        return Field(name, type=type, model_key='_id')

    if type == 'null':
        type = '*'

    return Field(name, type=type)


def build_resource_fields(parser):
    from .Resource import Resource
    from .Interface import Interface

    for cls in list_registered_classes():
        if issubclass(cls, (Resource, Interface)):
            schema = build_schema(cls, flatted=True)
            parser.import_fields_from_json_schema(schema, helper=custom_fields)


class ResourceQueryParser(Parser):

    def __init__(self, **kwargs):
        super(ResourceQueryParser, self).__init__(**kwargs)

        build_resource_fields(self)

    @staticmethod
    def check(expr):
        message = ''
        ok = True
        try:
            parser = ResourceQueryParser()
            parser.parse(expr)
        except:
            ok = False
            message = sys.exc_info()[1]

        return ok, message
