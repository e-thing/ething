# coding: utf-8
from future.utils import string_types, integer_types, with_metaclass

import re
import sys
from dateparser import parse
import datetime
from .Helpers import reraise
from future.utils import iteritems
import copy
import threading


class Validator(object):

    def validate(self, value, object):
        """
        Validate a value against this type and return a must return a sanitized value
        """
        raise NotImplementedError()

    def schema(self):
        """
        return a JSON schema describing this type
        """
        raise NotImplementedError()

    def __or__(self, other):
        return Or(self, other)

    def __and__(self, other):
        return And(self, other)


class Or(Validator):

    def __init__(self, *args):
        self.items = []
        for i in args:
            if isinstance(i, Or):
                for j in i.items:
                    self.items.append(j)
            else:
                self.items.append(i)

    def validate(self, value, object):
        errors = []
        for i in self.items:
            try:
                return i.validate(value, object)
            except Exception as e:
                errors.append(e)

        if errors:
            raise errors[0]

        return value

    def schema(self):
        schemas = []
        for i in self.items:
            try:
                schemas.append(i.schema())
            except NotImplementedError:
                pass

        if len(schemas) == 0:
            return {}
        else:
            return {
                "anyOf": schemas
            } if len(schemas) > 1 else schemas[0]


class And(Validator):

    def __init__(self, *args):
        self.items = []
        for i in args:
            if isinstance(i, And):
                for j in i.items:
                    self.items.append(j)
            else:
                self.items.append(i)

    def validate(self, value, object):
        sanitized_value = value
        for i in self.items:
            sanitized_value = i.validate(value, object)
        return sanitized_value

    def schema(self):
        schemas = []
        for i in self.items:
            try:
                schemas.append(i.schema())
            except NotImplementedError:
                pass

        if len(schemas) == 0:
            return {}
        else:
            return {
                "allOf": schemas
            } if len(schemas) > 1 else schemas[0]


class isAnything(Validator):

    def validate(self, value, object):
        return value

    def schema(self):
        return {}


class isNone(Validator):

    def validate(self, value, object):
        if value is not None:
            raise ValueError('not None')
        return value

    def schema(self):
        return {"type": "null"}


class isBool(Validator):

    def validate(self, value, object):
        if not isinstance(value, bool):
            raise ValueError('not a boolean')
        return value

    def schema(self):
        return {"type": "boolean"}


class isEnum(Validator):
    def __init__(self, enum):
        self.enum = enum

    def validate(self, value, object):
        if value not in self.enum:
            raise ValueError("must be one of the following values: %s." %
                             ','.join(str(e) for e in self.enum))
        return value

    def schema(self):
        return {"enum": self.enum}


class isNumber(Validator):

    def __init__(self, min=None, max=None):
        self.min = min
        self.max = max

    def validate(self, value, object):
        if not isinstance(value, integer_types) and not isinstance(value, float):
            raise ValueError('not a number')
        if self.min is not None:
            if value < self.min:
                raise ValueError('value < %s' % str(self.min))
        if self.max is not None:
            if value > self.max:
                raise ValueError('value > %s' % str(self.max))
        return value

    def schema(self):
        schema = {"type": "number"}
        if self.min is not None:
            schema['minimum'] = self.min
        if self.max is not None:
            schema['maximum'] = self.max
        return schema


class isInteger(isNumber):

    def validate(self, value, object):
        if not isinstance(value, integer_types):
            raise ValueError('not an integer')
        return super(isInteger, self).validate(value, object)

    def schema(self):
        schema = super(isInteger, self).schema()
        schema['type'] = 'integer'
        return schema


class isInstance(Validator):

    def __init__(self, cls):
        self.cls = cls

    def validate(self, value, object):
        if not isinstance(value, self.cls):
            raise ValueError('not an instance of "%s"' % self.cls.__name__)
        return value


class isDate(Validator):

    def validate(self, value, object):
        """
        return a Datetime
        """
        if isinstance(value, string_types):
            try:
                value = parse(value, languages=['en'])
            except:
                pass

        if not isinstance(value, datetime.datetime):
            raise ValueError('not a date')

        return value

    def schema(self):
        return {
            "type": "string",
            "format": "date-time"
        }


class isString(Validator):

    def __init__(self, allow_empty=True, regex=None, enum=None):
        self.allow_empty = allow_empty
        self.enum = enum
        self.regex = None
        if regex:
            if isinstance(regex, string_types):
                self.regex = regex
                pattern = regex
                flags = 0
            else:  # tupple
                pattern, flags = regex
                self.regex = str(regex)
                if isinstance(flags, string_types):
                    f = 0
                    for c in flags:
                        f = f | getattr(re, c.upper())
                    flags = f

            self.regex_c = re.compile(pattern, flags)

    def validate(self, value, object):
        if not isinstance(value, string_types):
            raise ValueError('not a string')

        if not self.allow_empty and len(value) == 0:
            raise ValueError('empty string')

        if self.regex is not None:
            if not self.regex_c.search(value):
                raise ValueError(
                    "does not match the regular expression '%s'" % self.regex)

        if self.enum is not None:
            if value not in self.enum:
                raise ValueError(
                    "must be one of the following values: %s." % ','.join(self.enum))

        return value

    def schema(self):
        schema = {"type": "string"}
        if not self.allow_empty:
            schema['minLength'] = 1
        if self.enum is not None:
            schema['enum'] = self.enum
        if self.regex is not None:
            schema['pattern'] = self.regex_c.pattern
        return schema


class isEmail(isString):

    USER_REGEX = re.compile(
        r"(^[-!#$%&'*+/=?^`{}|~\w]+(\.[-!#$%&'*+/=?^`{}|~\w]+)*$"  # dot-atom
        # quoted-string
        r'|^"([\001-\010\013\014\016-\037!#-\[\]-\177]'
        r'|\\[\001-\011\013\014\016-\177])*"$)', re.IGNORECASE | re.UNICODE)

    DOMAIN_REGEX = re.compile(
        # domain
        r'(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+'
        r'(?:[A-Z]{2,6}|[A-Z0-9-]{2,})$'
        # literal form, ipv4 address (SMTP 4.1.3)
        r'|^\[(25[0-5]|2[0-4]\d|[0-1]?\d?\d)'
        r'(\.(25[0-5]|2[0-4]\d|[0-1]?\d?\d)){3}\]$', re.IGNORECASE | re.UNICODE)

    DOMAIN_WHITELIST = ('localhost',)

    def __init__(self):
        super(isEmail, self).__init__(allow_empty=False)

    def validate(self, value, object):

        message = "not an email"

        super(isEmail, self).validate(value, object)

        if '@' not in value:
            raise ValueError(message)

        user_part, domain_part = value.rsplit('@', 1)

        if not self.USER_REGEX.match(user_part):
            raise ValueError(message)

        if domain_part not in self.DOMAIN_WHITELIST:
            if not self.DOMAIN_REGEX.match(domain_part):
                try:
                    domain_part = domain_part.encode('idna').decode('ascii')
                except UnicodeError:
                    pass
                else:
                    if self.DOMAIN_REGEX.match(domain_part):
                        return value
                raise ValueError(message)

        return value

    def schema(self):
        return {
            "type": "string",
            "format": "email"
        }


class isObject(Validator):

    def __init__(self, allow_extra=False, optionals=None, **kwargs):
        self.dict = kwargs
        self.allow_extra = allow_extra
        self.optionals = optionals or []

    def validate(self, value, object):
        if not isinstance(value, dict):
            raise ValueError('not an object')

        checked = []
        sanitized_value = {}
        for k, v in iteritems(value):

            validator = None

            if k in self.dict:
                validator = self.dict[k]
            else:
                if self.allow_extra is False:
                    raise ValueError("unknown key '%s'" % k)
                else:
                    validator = self.allow_extra

            if validator:
                try:
                    sanitized_value[k] = validator.validate(v, object)
                except Exception as e:
                    reraise(type(e), type(e)(
                        ("key '%s': " % k) + str(e)), sys.exc_info()[2])

            checked.append(k)

        for k, v in iteritems(self.dict):
            if k not in checked:
                if k not in self.optionals:
                    raise ValueError("the key '%s' is not present" % k)

        return sanitized_value

    def schema(self):
        schema = {"type": "object"}
        schema['additionalProperties'] = self.allow_extra if isinstance(
            self.allow_extra, bool) else self.allow_extra.schema()
        required = []
        schema['properties'] = {}
        for k, v in iteritems(self.dict):
            if k not in self.optionals:
                required.append(k)
            schema['properties'][k] = v.schema()
        if required:
            schema['required'] = required
        return schema


class isArray(Validator):

    def __init__(self, item=None, min_len=None, max_len=None):
        self.item = item
        self.min_len = min_len
        self.max_len = max_len

    def validate(self, value, object):
        if not isinstance(value, list):
            raise ValueError('not an array')

        l = len(value)

        if self.min_len is not None:
            if l < self.min_len:
                raise ValueError(
                    'the array must contain at least %d items (got %d)' % (self.min_len, l))

        if self.max_len is not None:
            if l > self.max_len:
                raise ValueError(
                    'the array must contain at most %d items (got %d)' % (self.max_len, l))

        if l > 0 and self.item is not None:
            sanitized_values = []
            for i in range(0, len(value)):
                try:
                    sanitized_values.append(
                        self.item.validate(value[i], object))
                except Exception as e:
                    reraise(type(e), type(e)(
                        ("the array item at index %d is invalid: " % i) + str(e)), sys.exc_info()[2])
            value = sanitized_values

        return value

    def schema(self):
        schema = {"type": "array"}
        schema['items'] = self.item.schema(
        ) if self.item is not None else isAnything().schema()
        if self.min_len is not None:
            schema['minItems'] = self.min_len
        if self.max_len is not None:
            schema['maxItems'] = self.max_len
        return schema


_type_map_ = {
    'int': isInteger(),
    'long': isInteger(),
    'float': isNumber(),
    'str': isString(),
    'unicode': isString(),
    'basestring': isString(),
    'bool': isBool(),
    'tuple': isArray(),
    'list': isArray(),
    'set': isArray(),
    'frozenset': isArray(),
    'dict': isObject(allow_extra=True),
    'none': isNone(),
    'NoneType': isNone(),
    'datetime': isDate(),
}


# decorator

READ_ONLY = 2
PRIVATE = 4


class ModelAdapter(object):

    def set(self, data_object, data, name, value):
        data[name] = value

    def get(self, data_object, data, name):
        return data.get(name)

    def has(self, data_object, data, name):
        return name in data


class NestedAdapter(ModelAdapter):
    """
    used to create nested model
    """

    def __init__(self, cls):
        self.cls = cls

    def _inherit(self, data_object):
        return {}  # will be transmitted to the constructor !

    def set(self, data_object, data, name, value):

        if isinstance(value, self.cls):
            instance = value
        else:
            if not isinstance(value, dict):
                raise ValueError('must be an object')

            if self.has(data_object, data, name):
                # update
                instance = self.get(data_object, data, name)
                instance.save(value)
            else:
                # create
                instance = self.cls.create(
                    value, **(self._inherit(data_object)))

        data[name] = instance.serialize()

    def get(self, data_object, data, name):
        return self.cls.unserialize(data.get(name), **(self._inherit(data_object)))


default_model_adapter = ModelAdapter()


def attr(name, validator=None, mode=None, **kwargs):
    def d(cls):

        attributes = getattr(cls, '__attributes', {})

        attributes_cls = getattr(cls, '__attributes_cls', None)
        if attributes_cls is not None and attributes_cls != cls.__name__:
            copy_attr = {}
            for n in attributes:
                copy_attr[n] = attributes[n].copy()
            attributes = copy_attr

        attributes.setdefault(name, {
            'model_adapter': default_model_adapter,
            'model_key': name,
            'classes': [],
            'on_change': None
        })

        if validator is not None:
            attributes[name]['validator'] = validator

        if mode is not None:
            attributes[name]['mode'] = mode

        required = False

        for i in kwargs:
            if i == 'default':
                kwargs[i] = _make_default_fct(kwargs[i])
            if i == 'required':
                required = kwargs[i]
            else:
                attributes[name][i] = kwargs[i]

        # remove the default attribute !
        if required:
            if 'default' in attributes[name]:
                attributes[name].pop('default')

        attributes[name]['classes'].append(cls)

        setattr(cls, '__attributes', attributes)
        setattr(cls, '__attributes_cls', cls.__name__)

        return cls
    return d


def abstract(cls):
    setattr(cls, '__abstract', True)
    return cls


def _make_default_fct(v):
    if callable(v):
        return v
    return lambda _: copy.deepcopy(v)


class MetaDataObject(type):

    """MetaDataObject metaclass"""

    def __init__(cls, nom, bases, dict):
        type.__init__(cls, nom, bases, dict)

        # do not propagate the __abstract attributes
        if hasattr(cls, '__abstract'):
            setattr(cls, '__abstract', False)


class DataObject(with_metaclass(MetaDataObject, object)):

    @classmethod
    def is_abstract(cls):
        return getattr(cls, '__abstract', False)

    def __init__(self, data=None):
        # make some private fields
        object.__setattr__(self, '_DataObject__new', data is None)
        object.__setattr__(self, '_DataObject__no_save', 0)
        object.__setattr__(self, '_DataObject__d', data or {})
        object.__setattr__(self, '_DataObject__dirtyFields', set())
        object.__setattr__(self, '_DataObject__lock', threading.Lock())

        if data is None:
            attributes = getattr(self, '__attributes', {})
            for name in attributes:
                attribute = attributes[name]
                if 'default' in attribute:
                    attribute['model_adapter'].set(
                        self, self.__d, attribute['model_key'], attribute['default'](self.__class__))

    def toJson(self):
        j = {}
        attributes = getattr(self, '__attributes', {})
        for name in attributes:
            attribute = attributes[name]
            if attribute.get('mode') == PRIVATE:
                continue
            model_adapter = attribute['model_adapter']
            try:
                j[name] = model_adapter.get(
                    self, self.__d, attribute['model_key'])
            except:
                pass
        return j

    def __getattr__(self, name):

        priv_access = False

        if name.startswith('_'):
            priv_access = True
            name = name[1:]

        attribute = getattr(self, '__attributes', {}).get(name)

        if attribute is None:
            raise AttributeError('no attribute "%s"' % name)

        if attribute.get('mode') == PRIVATE and not priv_access:
            raise AttributeError('attribute "%s" is not readable' % name)

        model_adapter = attribute['model_adapter']

        if not model_adapter.has(self, self.__d, attribute['model_key']):
            if 'default' in attribute:
                model_adapter.set(
                    self, self.__d, attribute['model_key'], attribute['default'](self.__class__))
            else:  # mandatory but not set
                raise AttributeError('attribute "%s" is not set' % name)

        return model_adapter.get(self, self.__d, attribute['model_key'])

    def __setattr__(self, name, value):

        priv_access = False

        if name.startswith('_'):
            priv_access = True
            name = name[1:]

        attribute = getattr(self, '__attributes', {}).get(name)

        if attribute is None:
            raise AttributeError('no attribute "%s"' % name)

        model_adapter = attribute['model_adapter']

        mode = attribute.get('mode')
        if (mode == PRIVATE or mode == READ_ONLY) and not priv_access:

            if mode == READ_ONLY:
                if model_adapter.has(self, self.__d, attribute['model_key']):
                    if value == model_adapter.get(self, self.__d, attribute['model_key']):
                        return  # do not raise an error if we want to write a read_only attribute with the same value !

            raise AttributeError('attribute "%s" is not writable' % name)

        validator = attribute.get('validator')
        if validator:
            try:
                value = validator.validate(value, self)
            except ValueError as e:
                raise AttributeError(
                    'invalid attribute "%s": %s' % (name, str(e)))

        on_change = attribute.get('on_change')
        if on_change:
            old_value = model_adapter.get(
                self, self.__d, attribute['model_key'])
            on_change(self, value, old_value)

        try:
            model_adapter.set(self, self.__d, attribute['model_key'], value)
        except ValueError as e:
            raise AttributeError('invalid attribute "%s": %s' % (name, str(e)))

        self.setDirtyAttr(name)

    def setDirtyAttr(self, name):
        self.__dirtyFields.add(name)

    def hasDirtyAttr(self):
        return bool(len(self.__dirtyFields))

    def getDirtyAttr(self):
        return self.__dirtyFields

    def save(self, attributes=None):

        if attributes is not None:
            for key, value in iteritems(attributes):
                setattr(self, key, value)

        if len(self.__dirtyFields) == 0 and not self.__new:
            return  # nothing to save

        if self.__no_save > 0:
            return

        # avoid infinit loop, if save() is called in _insert or _save
        object.__setattr__(self, '_DataObject__no_save', 1)

        try:

            if self.__new:

                attributes = getattr(self, '__attributes', {})
                for name in attributes:
                    attribute = attributes[name]

                    model_adapter = attribute.get('model_adapter', name)

                    if not model_adapter.has(self, self.__d, attribute['model_key']):
                        raise AttributeError(
                            'attribute "%s" is not set' % name)

                self._insert(self.__d)

                object.__setattr__(self, '_DataObject__new', False)

            else:
                self._save(self.__d)

            self.__dirtyFields.clear()

        except:
            raise
        finally:
            object.__setattr__(self, '_DataObject__no_save', 0)

    def _insert(self, data):
        raise NotImplementedError()

    def _save(self, data):
        raise NotImplementedError()

    def _refresh(self):
        raise NotImplementedError()

    def refresh(self, keepDirtyFields=False):
        doc = self._refresh()

        if keepDirtyFields:
            for field in self.__dirtyFields:
                try:
                    doc.pop(field)
                except KeyError:
                    pass

            self.__d.update(doc)
        else:
            self.__dirtyFields.clear()
            self.__d.clear()
            self.__d.update(doc)

    def __enter__(self):
        self.__lock.acquire()
        # necessary to take into account nested with statements
        object.__setattr__(self, '_DataObject__no_save', self.__no_save + 1)
        return self

    def __exit__(self, type, value, traceback):
        # necessary to take into account nested with statements
        object.__setattr__(self, '_DataObject__no_save', self.__no_save - 1)
        self.save()
        self.__lock.release()

    @classmethod
    def schema(cls, flatted=True, helper=None):
        schema = {
            "type": "object",
            "properties": {}
        }

        required = []

        description = cls.__doc__ or ''
        description = description.strip()

        attributes = getattr(cls, '__attributes', {})
        for attr_name in list(attributes):
            attribute = attributes.get(attr_name)
            mode = attribute.get('mode')

            if (not flatted) and (cls not in attribute.get('classes')):
                continue

            if mode == PRIVATE:
                continue

            attr_schema = {}
            schema_from_default_value = False
            validator = attribute.get('validator')
            if validator:
                try:
                    attr_schema = validator.schema()
                except NotImplementedError:
                    schema_from_default_value = True
            else:
                schema_from_default_value = True

            if 'default' in attribute:
                default = attribute['default'](cls)

                if schema_from_default_value:
                    validator = _type_map_.get(type(default).__name__)
                    if validator:
                        try:
                            attr_schema = validator.schema()
                        except NotImplementedError:
                            pass

                if isinstance(default, datetime.datetime):
                    default = default.isoformat()

                if mode != READ_ONLY:
                    attr_schema['default'] = default
            else:
                required.append(attr_name)

            if 'description' in attribute:
                attr_schema['description'] = attribute['description']

            if callable(helper):
                if helper(schema=attr_schema, name=attr_name, attribute=attribute) is False:
                    continue

            schema['properties'][attr_name] = attr_schema

        if required:
            schema['required'] = required

        if description:
            schema['description'] = description

        return schema

    def serialize(self):
        return self.__d

    @classmethod
    def unserialize(cls, data):
        return cls(data=data)

    @classmethod
    def create(cls, attributes, **ctor_attr):
        if cls.is_abstract():
            raise Exception(
                'Unable to create a new instance of the abstract class %s' % cls.__name__)

        instance = cls(**ctor_attr)
        instance.save(attributes)
        return instance
