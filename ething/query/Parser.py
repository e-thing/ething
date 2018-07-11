# coding: utf-8


# replace bool by boolean

"""

This class will parse a query string into a MongoDB query object used to filter a collection.


 
"""

import unicodedata
import re
import sys
from .Value import Value
from .Field import Field
from .Operator import Operator, EqualOperator, NotEqualOperator, ExistOperator, IsOperator, LowerOperator, GreaterOperator, LowerOrEqualOperator, GreaterOrEqualOperator, StartWithOperator, EndWithOperator, ContainOperator, ContainWordOperator, HasOperator
from .Stream import Stream
from .InvalidQueryException import InvalidQueryException
from future.utils import iteritems, listvalues
import ast


def get_type_from_json_schema(schema):

    type = schema.get('type')
    format = schema.get('format')

    if type is None:
        if 'anyOf' in schema or 'oneOf' in schema:
            types = []
            for s in schema['anyOf' if 'anyOf' in schema else 'oneOf']:
                t = get_type_from_json_schema(s)
                if isinstance(t, list):
                    types += t
                elif t == '*':
                    return t
                else:
                    types.append(t)
            return list(set(types))
        elif 'allOf' in schema:
            for s in schema['allOf']:
                t = get_type_from_json_schema(s)
                if t != '*':
                    return t

    if type == 'string':
        if format == "date-time":
            return "date"

    if type is None:
        return '*'

    return type


class Parser(object):

    def __init__(self, fields=None, constants=None, tz = None):

        self.tz = tz
        self.rules = []
        self.fields = {}
        self.constants = {}
        self.operators = {}
        self.fieldFallback = None

        # set defaults operators
        self.addOperator([
            EqualOperator(),
            NotEqualOperator(),
            ExistOperator(),
            IsOperator(),
            LowerOperator(),
            GreaterOperator(),
            LowerOrEqualOperator(),
            GreaterOrEqualOperator(),
            StartWithOperator(),
            EndWithOperator(),
            ContainOperator(),
            ContainWordOperator(),
            HasOperator(),
        ])

        self.addConstant('null', None)

        if fields:
            self.addField(fields)

        if constants:
            self.addConstant(constants)

    def addConstant(self, name, value=None):
        if isinstance(name, dict):
            for key, value in iteritems(name):
                self.constants[key] = value
        else:
            self.constants[name] = value

    def getConstant(self, name=None):
        if name is None:
            return listvalues(self.constants)
        if name in self.constants:
            return self.constants[name]
        return None

    def addField(self, field):
        if isinstance(field, list):
            for value in field:
                self.addField(value)
        else:
            self.fields[field.name] = field

    def getField(self, name):
        if name is None:
            return listvalues(self.fields)
        if name in self.fields:
            return self.fields[name]
        return None

    def addOperator(self, operator):
        if isinstance(operator, list):
            for value in operator:
                self.addOperator(value)
        else:
            self.operators[str(operator)] = operator

    def getOperator(self, syntax):
        if syntax is None:
            return listvalues(self.operators)
        if syntax in self.operators:
            return self.operators[syntax]
        return None

    def setFieldFallback(self, fallback):
        self.fieldFallback = fallback if callable(fallback) else None

    def add_field_rule(self, regexp, callback):
        self.rules.append({
            'regexp': regexp,
            're': re.compile(regexp),
            'callback': callback
        })

    def import_fields_from_json_schema(self, schema, name=None, helper=None):

        type = get_type_from_json_schema(schema)

        if type == 'object':

            properties = schema.get('properties', {})

            for prop_name in properties:
                self.import_fields_from_json_schema(
                    properties[prop_name], ("%s.%s" % (name, prop_name)) if name else prop_name)

            additionalProperties = schema.get('additionalProperties', True)

            if additionalProperties is not False:
                sub_type = None

                if isinstance(additionalProperties, dict):
                    sub_type = get_type_from_json_schema(additionalProperties)

                self.add_field_rule(
                    r'^%s.[^\.]+' % name, lambda field: Field(field, type=sub_type))

        if name:

            field = Field(name, type=type)

            if callable(helper):
                field = helper(name=name, type=type,
                               schema=schema, default_field=field)

            if isinstance(field, Field):
                self.addField(field)

    """
    Entry point
    """

    def parse(self, query):
        stream = Stream(query)
        return self.parseExpression(stream)

    def parseField(self, stream):
        stream.skipSpace()
        field = stream.read('[a-zA-Z0-9\.\-_]+')
        if field:
            if field in self.fields:
                return self.fields[field]
            else:

                for rule in self.rules:
                    if rule['re'].search(field):
                        f = rule['callback'](field)
                        if isinstance(f, Field):
                            return f

                if self.fieldFallback is not None:
                    f = self.fieldFallback(field)
                    if isinstance(f, Field):
                        return f
                raise InvalidQueryException(
                    "unknown field '%s'" % field, stream)
        else:
            raise InvalidQueryException('expected a field', stream)

    def parseOperator(self, stream):
        stream.skipSpace()
        op = stream.read('[\=\!\^\>\<\$\*~]+')
        if not op:
            op = stream.readWord()
        if op:
            if op in self.operators:
                return self.operators[op]
            else:
                raise InvalidQueryException(
                    "unknown operator '%s'" % op, stream)
        else:
            raise InvalidQueryException("expected an operator", stream)

    def parseValue(self, stream):
        stream.skipSpace()
        v = stream.read('^(?:\"([^\"]*(?:\"\"[^\"]*)*)\")')
        if not v:
            v = stream.read('^(?:\'([^\']*(?:\'\'[^\']*)*)\')')
        # try to get string (double quotes or simple quotes)
        if v:
            # quoted string

            return Value(self, ast.literal_eval(v))

            # r = v[1:-1] # remove the quotes
            # if(v[0] == '"'):
            #    r = r.decode('string_escape')
            #
            # return Value(self, r)

        else:
            v = stream.read('[a-zA-Z0-9\.\-_+]+')

            # number ? (integer or float)
            isNumber = False
            try:
                c = float(v)
                return Value(self, c)
            except ValueError:
                pass

            try:
                c = unicodedata.numeric(v)
                return Value(self, c)
            except (TypeError, ValueError):
                pass

            # boolean ?
            m = re.search('^True$', v, re.IGNORECASE)
            if m:
                return Value(self, True)
            m = re.search('^False$', v, re.IGNORECASE)
            if m:
                return Value(self, False)

            # maybe a CONSTANT
            if v in self.constants:
                return Value(self, self.constants[v])

            raise InvalidQueryException("invalid value '%s'" % v, stream)

    """
     parse a Field-Operator-Value expression
    """

    def parseFOV(self, stream):

        if stream.read('^\s*[nN][oO][tT]($|\s+)'):
            return {'$nor': [self.parseFOV(stream)]}

        field = self.parseField(stream)
        op = self.parseOperator(stream)
        value = self.parseValue(stream) if op.hasValue() else None

        if not op.accept(field, value):
            raise InvalidQueryException(
                "the operator '%s' is invalid" % op, stream)

        try:
            compiled = field.compil(op, value)
        except:
            raise InvalidQueryException(sys.exc_info()[1], stream)

        return compiled

    """
     Parse a FOV or a enclosed expression
    """

    def parseFragment(self, stream):
        if stream.read('^\s*\('):
            # start enclosure
            f = self.parseExpression(stream)

            # must be followed by a ')'
            if not stream.read('^\s*\)'):
                raise InvalidQueryException("expected a ')'", stream)

        else:
            f = self.parseFOV(stream)

        return f

    def parseExpression(self, stream):

        stack = []

        stream.skipSpace()

        if not stream.length() or stream.match('/^\)/'):
            raise InvalidQueryException('empty expression', stream)

        # get the first fragment
        stack.append(self.parseFragment(stream))

        # search for other FOV expressions separated by a logical operator
        while stream.length() > 0:

            stream.skipSpace()

            if not stream.length() or stream.match('^\)'):
                break  # the end

            # search for a logical operator
            logic = stream.read('^([aA][nN][dD]|[oO][rR])($|\s+)')
            if logic:
                stack.append(logic.strip().lower())
            else:
                raise InvalidQueryException(
                    'waiting for a logical operator', stream)

            # search for a fragment
            stack.append(self.parseFragment(stream))

        # compilation of the stack
        logicPrecedence = ['and', 'or']
        logicIndex = 0
        while len(stack) > 1:

            currentLogic = logicPrecedence[logicIndex]

            i = 0
            while i < len(stack):
                if stack[i] == currentLogic:
                    exp = {
                        '$'+currentLogic: [stack[i-1], stack[i+1]]
                    }

                    stack.pop(i+1)
                    stack.pop(i)
                    stack.pop(i-1)
                    stack.insert(i, exp)

                    i -= 1
                i += 1

            logicIndex += 1

            if logicIndex == len(logicPrecedence):
                if len(stack) > 1:
                    raise InvalidQueryException('error')
                break

        return stack[0]
