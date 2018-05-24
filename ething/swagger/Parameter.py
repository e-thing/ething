# coding: utf-8
from future.utils import string_types, integer_types


"""

todo:

allowEmptyValue
format


"""


def instanciate(paramobj, parent):

    if paramobj.get('in', None) == 'body':
        return BodyParameter(paramobj, parent)
    else:
        return StandardParameter(paramobj, parent)


class Parameter(object):

    def __init__(self, data, parent):
        self.__parent = parent
        self.data = data

    @property
    def root(self):
        return self.__parent.root

    @property
    def name(self):
        return self.data['name']

    @property
    def where(self):
        return self.data['in']

    @property
    def isRequired(self):
        return self.data.get('required', False)

    @property
    def description(self):
        return self.data.get('description', '')

    def validate(self, data):
        return True

    def toJsonSchema(self):
        return {
            'title': self.name,
            'description': self.description
        }


"""

todo:

allowEmptyValue
format


"""


class StandardParameter(Parameter):

    collectionFormatList = {
        'csv': ",",
        'ssv': " ",
        'tsv': "\t",
        'pipes': "|",
        "multi": "&"
    }

    def __init__(self, data, parent):
        super(StandardParameter, self).__init__(data, parent)

        if self.collectionFormat not in list(StandardParameter.collectionFormatList):
            raise Exception("invalid collectionFormat %s" %
                            str(self.collectionFormat))

    @property
    def type(self):
        return self.data['type']

    @property
    def hasDefault(self):
        return 'default' in self.data

    @property
    def defaultValue(self):
        return self.data.get('default', None)

    @property
    def collectionFormat(self):
        return self.data.get('collectionFormat', 'csv')

    def validate(self, data):

        return StandardParameter.validateType(self.data, data)

    jsonSchemaFields = [
        'type',
        'format',
        'items',
        'default',
        'maximum',
        'exclusiveMaximum',
        'minimum',
        'exclusiveMinimum',
        'maxLength',
        'minLength',
        'pattern',
        'maxItems',
        'minItems',
        'uniqueItems',
        'enum',
        'multipleOf'
    ]

    @staticmethod
    def filter(schema, where=None):

        if where is None:
            where = {}

        for field in StandardParameter.jsonSchemaFields:
            f = schema.get(field, None)
            if f is not None:
                where[field] = StandardParameter.filter(
                    f) if field == 'items' else f

        return where

    def toJsonSchema(self):
        # replace by a deep clone
        return StandardParameter.filter(self.data, super(StandardParameter, self).toJsonSchema())

    @staticmethod
    def validateType(options, value):
        type = options['type']

        if (value is None or (isinstance(value, string_types) and value == '')) and options.get('allowEmptyValue', False):
            return value

        if type == "string":

            if isinstance(value, integer_types) or isinstance(value, float) or isinstance(value, bool):
                value = str(value)

            if not isinstance(value, string_types):
                raise Exception("must be a string '%s'" % str(value))

        elif type == "number":

            try:
                v = float(value)
            except ValueError:
                raise Exception("must be a number '%s'" % str(value))

            value = v

        elif type == "integer":

            try:
                v = int(value)
            except ValueError:
                raise Exception("must be an integer '%s'" % str(value))

            value = v

        elif type == "boolean":

            if isinstance(value, string_types):
                if value.lower() == 'true':
                    value = True
                elif value.lower() == 'false':
                    value = False
                elif value == '1':
                    value = True
                elif value == '0':
                    value = False
            if isinstance(value, integer_types):
                if value == 0:
                    value = False
                else:
                    value = True
            if isinstance(value, float):
                if value == 0.:
                    value = False
                else:
                    value = True
            if value is None:
                value = False

            if not isinstance(value, bool):
                raise Exception("must be a boolean '%s'" % str(value))

        elif type == "array":

            if not isinstance(value, list):
                raise Exception("must be an array '%s'" % str(value))

            vv = []
            for v in value:
                vv.append(
                    str(StandardParameter.validateType(options['items'], v)))

            value = vv

            collectionFormat = options.get('collectionFormat', 'csv')

            if collectionFormat in list(StandardParameter.collectionFormatList):

                if collectionFormat != "multi":
                    value = StandardParameter.collectionFormatList[collectionFormat].join(
                        value)

        elif type == "file":

            if not isinstance(value, string_types):
                raise Exception("must be a string '%s'" % str(value))

        return value


"""

todo:

allowEmptyValue
format


"""


class BodyParameter(Parameter):

    nonJsonSchemaFields = [
        'discriminator',
        'readOnly',
        'xml',
        'externalDocs',
        'example'
    ]

    def __init__(self, data, parent):

        super(BodyParameter, self).__init__(data, parent)

        self.__schema = self.data['schema']

    @property
    def schema(self):
        return self.__schema

    def validate(self, data):
        return BodyParameter.validateSchema(self.data, data)

    def toJsonSchema(self):
        jsonSchema = super(BodyParameter, self).toJsonSchema()
        jsonSchema.update(self.schema)
        return jsonSchema

    @staticmethod
    def validateSchema(options, value, definitions=None):
        # todo !
        return value
