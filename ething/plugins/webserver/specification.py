# coding: utf-8

# used to build the HTTP API documentation
from __future__ import print_function
from future.utils import string_types
from .Scope import list as scope_list
import apispec
from ething.version import __version__
from ething.Resource import Resource
from ething.reg import *
import json
import jinja2
from codecs import open

try:
    from apispec.ext.flask import path_from_view
except ImportError:
    raise Exception('only work with apispec version=0.38.0')


from pkg_resources import parse_version
import copy
from apispec.ext.marshmallow import swagger
from marshmallow import Schema
from marshmallow.utils import is_instance_or_subclass


import os

template_file = os.path.abspath(os.path.join(
    os.path.dirname(__file__), 'api.md.j2'))
readme_file = os.path.abspath(os.path.join(
    os.path.dirname(__file__), 'readme.md'))

# --------------

import re
import werkzeug.routing

PATH_RE = re.compile(r'<(?:[^:<>]+:)?([^<>]+)>')


def rule_to_path(rule):
    return PATH_RE.sub(r'{\1}', rule.rule)


path_arguments = {
    'id': "An id representing a Resource",
    'operationId': "id of the operation",
    'customEventName': 'name of the custom event',
}

CONVERTER_MAPPING = {
    werkzeug.routing.UnicodeConverter: ('string', None),
    werkzeug.routing.IntegerConverter: ('integer', 'int32'),
    werkzeug.routing.FloatConverter: ('number', 'float'),
}

DEFAULT_TYPE = ('string', None)


def rule_to_params(rule, overrides=None):
    overrides = (overrides or {})
    result = [
        argument_to_param(argument, rule, overrides.get(argument, {}))
        for argument in rule.arguments
    ]
    for key in list(overrides):
        if overrides[key].get('in') in ('header', 'query'):
            overrides[key]['name'] = overrides[key].get('name', key)
            result.append(overrides[key])
    return result


def argument_to_param(argument, rule, override=None):
    param = {
        'in': 'path',
        'name': argument,
        'required': True,
    }

    cls = type(rule._converters[argument])

    description = path_arguments.get(argument)
    if description:
        param['description'] = description

    type_, format_ = CONVERTER_MAPPING.get(cls, DEFAULT_TYPE)
    param['type'] = type_
    if format_ is not None:
        param['format'] = format_
    if rule.defaults and argument in rule.defaults:
        param['default'] = rule.defaults[argument]
    param.update(override or {})
    return param


# --------------

def scopes_docs():
    s = """
### Scopes

Scopes let you specify exactly what type of data access an API key needs.

| Scope          | Description                                                          |
|----------------|----------------------------------------------------------------------|
"""

    for scope_name in scope_list:
        desc = scope_list[scope_name].get('description', '')
        s += '|%16s|%70s|\n' % ("`%s`" % scope_name, desc)

    return s


def generate(app, specification='stdout', documentation=None):

    core = app.core
    description = ''

    with open(readme_file, 'r') as content_file:
        description = content_file.read()

    description += '\n\n' + scopes_docs()

    spec = apispec.APISpec(
        title='EThing HTTP API',
        version=__version__,
        info=dict(
            description=description
        ),
        plugins=[
            # 'apispec.ext.flask',
            'apispec.ext.marshmallow',
        ],
        schemes=['http'],
        #basePath = '/api',
        consumes=['application/json'],
        produces=['application/json'],
        securityDefinitions={
            "api_key": {
                "type": "apiKey",
                "description": 'authentication through an API key, used only by devices or apps.',
                "name": "X-API-KEY",
                "in": "header",
            },
            "api_key_query": {
                "type": "apiKey",
                "description": 'authentication through an API key, used only by devices or apps.',
                "name": "api_key",
                "in": "query",
            },
            "basic_auth": {
                "type": "basic",
                "description": "basic authentication.",
            },
        },
        security=[
            {
                "api_key": []
            },
            {
                "api_key_query": []
            },
            {
                "basic_auth": []
            }
        ],
    )

    def my_path_from_view(spec, view, parameters=None, **kwargs):

        path = path_from_view(spec, view, **kwargs)

        if parameters:
            for method in list(path.operations):

                method_uppercase = method.upper()

                if method_uppercase not in parameters:
                    continue

                method_params = parameters.get(method_uppercase)

                path.operations[method].setdefault('parameters', [])

                current_params = path.operations[method].get('parameters')

                # merge !
                for p in method_params:
                    name = p.get('name')

                    # does this parameter already exist ?
                    exist = False
                    for _p in current_params:
                        if name == _p.get('name'):
                            exist = _p
                            break

                    if exist:
                        # merge, the parameter set in the docstring take precedence !
                        new_param = {}
                        new_param.update(p)
                        new_param.update(exist)
                        exist.update(new_param)
                    else:
                        # add it to the list of parameters
                        current_params.append(p)

        return path

    spec.register_path_helper(my_path_from_view)

    #
    # Generate definitions
    #

    def remove_kinfOf_attribute(schema):
        """
        openapi v2 does not handle anyOf or allOf or oneOf attributes !
        """
        while isinstance(schema, dict):
            if 'anyOf' in schema:
                anyOf = schema.pop('anyOf')
                schema.update(anyOf[0] if anyOf else {})
            elif 'oneOf' in schema:
                oneOf = schema.pop('oneOf')
                schema.update(oneOf[0] if oneOf else {})
            elif 'allOf' in schema:
                allOf = schema.pop('allOf')
                for i in allOf:
                    schema.update(i)
            else:
                break

    def resource_attr_helper(schema, name, attribute):

        if attribute.get('mode') == READ_ONLY:
            schema['$readOnly'] = True

        remove_kinfOf_attribute(schema)

        if 'additionalProperties' in schema:
            remove_kinfOf_attribute(schema['additionalProperties'])

        if schema.get('type') == "null":
            schema.pop('type')

        if name == 'modifiedDate' and 'default' in schema:
            schema['default'] = "<current date>"

    spec._definitions.update(build_schema_definitions(subclass=(Resource, ), no_methods = True, core=core))

    spec.definition("Error", description="An object describing an error", properties={
        "message": {
            "type": "string",
            "description": "A description of the error",
            "$readOnly": True
        },
        "code": {
            "type": "integer",
            "description": "The HTTP response status code",
            "$readOnly": True
        }
    }, extra_fields = {
        'type': 'object'
    })

    #
    # Generate the rules
    #
    for rule in app.url_map.iter_rules():

        if rule.endpoint == 'static':
            continue  # internal endpoints

        view = app.view_functions.get(rule.endpoint)

        if view and view.__doc__:

            with app.test_request_context():

                parameters = {}  # by methods
                webargs = getattr(view, 'webargs', None)

                for method in rule.methods:

                    method_params = rule_to_params(rule) or []

                    if webargs:

                        wa = webargs.get(method, webargs.get('*'))

                        if wa:
                            schema = wa.get('schema')
                            options = copy.copy(wa.get('options'))

                            if is_instance_or_subclass(schema, Schema):
                                converter = swagger.schema2parameters
                            elif callable(schema):
                                schema = schema(request=None)
                                if is_instance_or_subclass(schema, Schema):
                                    converter = swagger.schema2parameters
                                else:
                                    converter = swagger.fields2parameters
                            else:
                                converter = swagger.fields2parameters

                            location = options.pop(
                                'location', 'query')  # default to query
                            if location:
                                options['default_in'] = location
                            if parse_version(apispec.__version__) < parse_version('0.20.0'):
                                options['dump'] = False

                            extra_params = converter(schema, **options)

                            method_params = method_params + extra_params

                    parameters[method] = method_params

                spec.add_path(view=view, parameters=parameters)

    if callable(specification):
        specification(spec)
    elif specification == 'stdout':
        print(json.dumps(spec.to_dict(), indent=2))
    elif isinstance(specification, string_types):
        extension = os.path.splitext(specification)[1]
        f = open(specification, 'w')
        if extension == '.json':
            f.write(json.dumps(spec.to_dict(), indent=2))
        else:
            f.write(spec.to_yaml())
        f.close()

    env = jinja2.Environment(
        extensions=["jinja2.ext.do"], trim_blocks=True, lstrip_blocks=True)
    env.filters['get_headers'] = get_headers
    env.filters['make_id'] = make_id
    template = env.from_string(
        open(template_file, 'r', encoding="utf8").read())

    content = template.render(swagger_data=spec.to_dict())
    content = re.sub(r'\n\s*\n', '\n\n', content)

    if callable(documentation):
        documentation(content)
    elif documentation == 'stdout':
        print(content)
    elif isinstance(documentation, string_types):
        f = open(documentation, 'w')
        f.write(content)
        f.close()


def get_headers(input):

    headers = []
    rec = re.compile('^#+ *(.+) *$')
    for l in input.splitlines():
        m = rec.search(l)
        if m:
            headers.append(m.group(1))

    return headers


def make_id(str):
    """
    Convert `string` into an identifier and return it.
    """
    str = str.lower()
    str = re.sub('[^-a-zA-Z]+', '-', str)
    str = re.sub('^-|-$', '', str)
    return str
