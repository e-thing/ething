# coding: utf-8

from .query.Parser import Parser
from .query.Field import Field
from .meta import resource_classes
import sys


def custom_fields(name, type, schema, default_field):
    if name == 'id':
        return Field(name, type=type, model_key='_id')

    if type == 'null':
        type = '*'

    return Field(name, type=type)


def build_resource_fields(parser):

    for cls_name in resource_classes:
        cls = resource_classes[cls_name]

        schema = cls.schema(flatted=True)

        parser.import_fields_from_json_schema(schema, helper=custom_fields)


class ResourceQueryParser(Parser):

    def __init__(self):
        super(ResourceQueryParser, self).__init__()

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
