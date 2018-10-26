# coding: utf-8
from future.utils import string_types, integer_types
from collections import MutableSequence, Sequence, MutableMapping, Mapping, OrderedDict
import re
import datetime
from dateutil.parser import parse
import inspect


class Type (object):
  
  def __init__(self, **attributes):
    self._attributes = attributes
  
  def __getattr__(self, name):
    return self._attributes.get(name)
  
  def set(self, value, context = None):
    return value

  def get(self, value, context = None):
    return value
  
  def toJson(self, value, context = None):
    return value
  
  def fromJson(self, value, context = None):
    return value
  
  def serialize(self, value, context = None):
    return value
  
  def unserialize(self, value, context = None):
    return value
  
  def toSchema(self, context = None):
    s = {}
    if self.description:
      s['description'] = self.description
    if self.default is not None:
      s['default'] = self.default
    return s


class Memory (object):

  def __init__(self):
    object.__setattr__(self, '_Memory__dirty', False)
  
  def _set_dirty(self):
    object.__setattr__(self, '_Memory__dirty', True)
    
  def _is_dirty(self):
    dirty = self.__dirty
    if not dirty:
      for child in self._children():
        if child._is_dirty():
          dirty = True
          break
    return dirty
  
  def _children(self):
    return []
  
  def _clean(self):
    object.__setattr__(self, '_Memory__dirty', False)
    for child in self._children():
      child._clean()
  

class Nullable (Type):
  """
  accept None value plus the given type
  """
  def __init__(self, dtype, **attributes):
    super(Nullable, self).__init__(**attributes)
    self._type = convert_type(dtype)
  
  def set(self, value, context = None):
    return value if value is None else self._type.set(value, context)

  def get(self, value, context = None):
    return value if value is None else self._type.get(value, context)
  
  def toJson(self, value, context = None):
    return value if value is None else self._type.toJson(value, context)
  
  def fromJson(self, value, context = None):
    return value if value is None else self._type.fromJson(value, context)
  
  def serialize(self, value, context = None):
    return value if value is None else self._type.serialize(value, context)
  
  def unserialize(self, value, context = None):
    return value if value is None else self._type.unserialize(value, context)
  
  def toSchema(self, context = None):
    schema = super(Nullable, self).toSchema(context)

    schema['anyOf'] = [
      {
        'type': 'null'
      },
      self._type.toSchema(context)
    ]

    return schema


class Basetype(Type):
  
  def validate(self, data, context = None):
    pass
  
  def set(self, value, context = None):
    self.validate(value, context)
    return value
  
  def fromJson(self, value, context = None):
    self.validate(value, context)
    return value


class Scalar(Basetype):
    """
    accept any of the following types: null, number, string, boolean
    """

    def __init__(self, **attributes):
        super(Scalar, self).__init__(**attributes)

    def validate(self, value, context = None):
        if not ( (value is None) or isinstance(value, bool) or isinstance(value, float) or isinstance(value, integer_types) or isinstance(value, string_types)):
            raise ValueError('not of the following types: null, number, string, boolean')

    def toSchema(self, context = None):
        schema = super(Scalar, self).toSchema(context)

        schema['anyOf'] = [{
            'type': 'number'
        },{
            'type': 'string'
        },{
            'type': 'boolean'
        },{
            'type': 'null'
        }]

        return schema


class Null(Basetype):
    def __init__(self, **attributes):
        super(Null, self).__init__(**attributes)

    def validate(self, value, context = None):
        if value is not None:
            raise ValueError('not null')

    def toSchema(self, context = None):
        schema = super(Null, self).toSchema(context)
        schema['type'] = 'null'
        return schema


class Number(Basetype):
  
  def __init__(self, min=None, max=None, **attributes):
    super(Number, self).__init__(**attributes)
    self.min = min
    self.max = max
    
  def validate(self, value, context = None):
    if not isinstance(value, integer_types) and not isinstance(value, float):
      raise ValueError('not a number (%s)' % type(value).__name__)
    if self.min is not None:
      if value < self.min:
        raise ValueError('value < %s' % str(self.min))
    if self.max is not None:
      if value > self.max:
        raise ValueError('value > %s' % str(self.max))
  
  def toSchema(self, context = None):
    schema = super(Number, self).toSchema(context)
    schema['type'] = 'number'
    if self.min is not None:
        schema['minimum'] = self.min
    if self.max is not None:
        schema['maximum'] = self.max
    return schema


class Integer(Number):
    
  def validate(self, value, context = None):
    if not isinstance(value, integer_types):
      raise ValueError('not an integer')
    super(Integer, self).validate(value, context)

  def toSchema(self, context = None):
    schema = super(Integer, self).toSchema(context)
    schema['type'] = 'integer'
    return schema

class Boolean(Basetype):
  
  def __init__(self, **attributes):
    super(Boolean, self).__init__(**attributes)
    
  def validate(self, value, context = None):
    if not isinstance(value, bool):
      raise ValueError('not a boolean')
  
  def toSchema(self, context = None):
    schema = super(Boolean, self).toSchema(context)
    schema['type'] = 'boolean'
    return schema

class Enum(Basetype):
  
  def __init__(self, enum, **attributes):
    super(Enum, self).__init__(**attributes)
    self.enum = enum
    
  def validate(self, value, context = None):
    if value not in self.enum:
      raise ValueError("must be one of the following values: %s." %
                        ','.join(str(e) for e in self.enum))
  
  def toSchema(self, context = None):
    schema = super(Enum, self).toSchema(context)
    schema['enum'] = self.enum
    return schema

class String(Basetype):
  
  def __init__(self, allow_empty=True, regex=None, enum=None, maxLength = None, **attributes):
    super(String, self).__init__(**attributes)
    self.allow_empty = allow_empty
    self.enum = enum
    self.maxLength = maxLength
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
    
  def validate(self, value, context = None):
    
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

    if self.maxLength is not None:
      if len(value) > self.maxLength:
        raise ValueError(
          "the length must not be greater than %d" % self.maxLength)
  
  def toSchema(self, context = None):
    schema = super(String, self).toSchema(context)
    schema['type'] = 'string'
    if not self.allow_empty:
      schema['minLength'] = 1
    if self.enum is not None:
      schema['enum'] = self.enum
    if self.regex is not None:
      schema['pattern'] = self.regex_c.pattern
    if self.maxLength is not None:
      schema['maxLength'] = self.maxLength
    return schema

class Email(String):
  
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

  DOMAIN_WHITELIST = ("localhost",)
  
  def __init__(self, **attributes):
    super(Email, self).__init__(allow_empty=False, **attributes)
  
  def validate(self, value, context = None):
    
    message = "not an email"

    super(Email, self).validate(value, context)

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
  
  def toSchema(self, context = None):
    schema = super(Email, self).toSchema(context)
    schema['type'] = 'string'
    schema['format'] = 'email'
    return schema


class Date(Basetype):
  
  def validate(self, value, context = None):
    if not isinstance(value, datetime.datetime):
      raise ValueError('not a date')
  
  def toSchema(self, context = None):
    schema = super(Date, self).toSchema(context)
    schema['type'] = 'string'
    schema['format'] = 'date-time'
    return schema
  
  def toJson(self, value, context = None):
    return value
  
  def fromJson(self, value, context = None):
    value = parse(value, languages=['en'])
    self.validate(value, context)
    return value
  

class Color(String):
  def __init__(self, **attributes):
    super(Color, self).__init__(regex = '^#[0-9a-fA-F]{6}$', **attributes)

  def toSchema(self, context = None):
    schema = super(Color, self).toSchema(context)
    schema['type'] = 'string'
    schema['format'] = 'color'
    return schema


class Array(Type):

  def __init__(self, item_type = Basetype(), min_len=None, max_len=None, **attributes):
    super(Array, self).__init__(**attributes)
    self.item_type = convert_type(item_type)
    self.min_len = min_len
    self.max_len = max_len
  
  def validate(self, data, context = None):
    if not isinstance(data, Sequence) and not isinstance(data, string_types):
      raise ValueError('not an array')
    
    # check size
    l = len(data)

    if self.min_len is not None:
      if l < self.min_len:
          raise ValueError(
              'the array must contain at least %d items (got %d)' % (self.min_len, l))

    if self.max_len is not None:
        if l > self.max_len:
            raise ValueError(
                'the array must contain at most %d items (got %d)' % (self.max_len, l))
  
  def set(self, value, context = None):
    if not (isinstance(value, M_Array) and value._type is self):
      if isinstance(value, Sequence) and not isinstance(value, string_types):
        value = M_Array(self, value, context)
      else:
        raise ValueError('not an array')
    return value

  def unserialize(self, data, context = None):
      return [self.item_type.unserialize(el, context) for el in data]

  def serialize(self, value, context = None):
    return [self.item_type.serialize(el, context) for el in value]
  
  def fromJson(self, data, context = None):
      self.validate(data, context)
      return [self.item_type.fromJson(el, context) for el in data]
  
  def toJson(self, value, context = None):
    return [self.item_type.toJson(el, context) for el in value]
  
  def toSchema(self, context = None):
    schema = super(Array, self).toSchema(context)
    schema['type'] = 'array'
    schema['items'] = self.item_type.toSchema(context)
    if self.min_len is not None:
      schema['minItems'] = self.min_len
    if self.max_len is not None:
      schema['maxItems'] = self.max_len
    return schema

  
class M_Array(Memory, MutableSequence):

    def __init__(self, dtype, value = None, context = None):
      if value is None:
        value = []

      Memory.__init__(self)
      self._list = list()
      self._type = dtype
      self._context = context

      self._type.validate(value, context)

      for el in value:
        self._list.append(self._type.item_type.set(el, context))

    def __len__(self): return len(self._list)

    def __getitem__(self, i): return self._type.item_type.get(self._list[i], self._context)

    def __delitem__(self, i):
      if self._type.min_len is not None:
        l = len(self._list)
        if l == self._type.min_len:
            raise ValueError(
                'the array must contain at least %d items' % (self._type.min_len))
      
      del self._list[i]
      self._set_dirty()

    def __setitem__(self, i, val):
      self._list[i] = self._type.item_type.set(val, self._context)
      self._set_dirty()

    def insert(self, i, val):
      if self._type.max_len is not None:
        l = len(self._list)
        if l > self._type.max_len:
            raise ValueError(
                'the array must contain at most %d items' % (self._type.max_len))
      
      self._list.insert(i, self._type.item_type.set(val, self._context))
      self._set_dirty()

    def __str__(self):
        return str(self._list)
    
    def _children(self):
      return [ item for item in self._list if isinstance(item, Memory) ]


class Dict(Type):

  def __init__(self, allow_extra=None, optionals=None, mapping = None, **attributes):
    super(Dict, self).__init__(**attributes)

    if allow_extra is None:
        allow_extra = bool(mapping is None)

    self.allow_extra = allow_extra if isinstance(allow_extra, bool) else convert_type(allow_extra)
    self.optionals = optionals or []
    self.mapping = OrderedDict()
    if mapping is not None:
        for k in mapping:
          self.mapping[k] = convert_type(mapping[k])
  
  def get_type_from_key(self, key):
    if key in self.mapping:
      return self.mapping[key]
    if self.allow_extra:
      if isinstance(self.allow_extra, Type):
        return self.allow_extra
      return Basetype()
    raise KeyError('invalid key %s' % key)
  
  def validate(self, data, context = None):
    if not isinstance(data, Mapping):
      raise ValueError('not an object')
    
    for key in data:
      self.get_type_from_key(key) # will throw an error if the key is invalid !

    # check for missing keys
    for key in self.mapping:
      if key not in data:
        if key not in self.optionals:
          raise ValueError("the key '%s' is not present" % key)
  
  def set(self, value, context = None):
    if not (isinstance(value, M_Dict) and value._type is self):
      if isinstance(value, Mapping):
        value = M_Dict(self, value, context)
      else :
        raise ValueError('not an object, got %s' % type(value).__name__)
    return value

  def unserialize(self, data, context = None):
    j = {}
    for key in data:
      item_type = self.get_type_from_key(key)
      j[key] = item_type.unserialize(data.get(key), context)
    return j
  
  def serialize(self, value, context = None):
    j = {}
    for key in value:
      item_type = self.get_type_from_key(key)
      j[key] = item_type.serialize(value[key], context)
    return j
  
  def fromJson(self, data, context = None):
    self.validate(data, context)
    j = {}
    for key in data:
      item_type = self.get_type_from_key(key)
      j[key] = item_type.fromJson(data.get(key), context)
    return j
  
  def toJson(self, value, context = None):
    j = {}
    for key in value:
      item_type = self.get_type_from_key(key)
      j[key] = item_type.toJson(value[key], context)
    return j
  
  def toSchema(self, context = None):
    schema = super(Dict, self).toSchema(context)
    schema['type'] = 'object'
    schema['additionalProperties'] = self.allow_extra if isinstance(self.allow_extra, bool) else self.allow_extra.toSchema(context)
    required = []
    schema['properties'] = OrderedDict()
    for key in self.mapping:
      if key not in self.optionals:
          required.append(key)
      schema['properties'][key] = self.mapping[key].toSchema(context)
    if required:
      schema['required'] = required
    return schema


class M_Dict(Memory, MutableMapping):

  def __init__(self, dtype, value = None, context = None):
    if value is None:
      value = []
    Memory.__init__(self)
    self._store = dict()
    self._type = dtype
    self._context = context

    self._type.validate(value, context)

    for i in value:
      self.__setitem__(i, value[i])

  def __getitem__(self, key):
    item_type = self._type.get_type_from_key(key)
    return item_type.get(self._store[key], self._context)

  def __setitem__(self, key, value):
    item_type = self._type.get_type_from_key(key)
    self._store[key] = item_type.set(value, self._context)
    self._set_dirty()

  def __delitem__(self, key):
    if key not in self._type.optionals:
      raise ValueError("the key '%s' is mandatory" % key)
    del self._store[key]
    self._set_dirty()

  def __iter__(self):
    return iter(self._store)

  def __len__(self):
    return len(self._store)
  
  def __str__(self):
    return str(self._store)
  
  def _children(self):
      return [ item for item in self._store.values() if isinstance(item, Memory) ]


class Class (Type):

  def __init__(self, cls, **attributes):
    super(Class, self).__init__(**attributes)
    self.cls = cls
  
  def set(self, value, context = None):
    if not isinstance(value, self.cls):
      raise ValueError('not an instance of %s' % self.cls.__name__)
    return value
  
  def unserialize(self, data, context = None):
    return self.cls.unserialize(data, context)
  
  def serialize(self, value, context = None):
    return value.serialize(context)

  def fromJson(self, data, context = None):
    return self.cls.fromJson(data, context)

  def toJson(self, value, context = None):
    return value.toJson(context)
  
  def toSchema(self, context = None):
    return self.cls.toSchema(context)


class M_Class(Memory):

  def toJson(self, context = None):
    raise NotImplementedError()
  
  def serialize(self, context = None):
    raise NotImplementedError()
  
  @classmethod
  def unserialize(cls, data, context = None):
    raise NotImplementedError()
  
  @classmethod
  def fromJson(cls, data, context = None):
    raise NotImplementedError()
  
  @classmethod
  def toSchema(cls, context = None):
    raise NotImplementedError()

_none_type_class = type(None)

def convert_type(t):
  """
  converts the givent argument to the right type
  """

  if isinstance(t, Type):
    return t
  
  if isinstance(t, string_types):
    if t in _type_map_:
      return _type_map_[t]
    else:
      raise Exception('unknown type "%s"' % t)
  
  if inspect.isclass(t):

    if issubclass(t, _none_type_class):
      return Null()
    if issubclass(t, bool):
      return Boolean()
    if issubclass(t, integer_types):
      return Integer()
    if issubclass(t, float):
      return Number()
    if issubclass(t, string_types):
      return String()
    if issubclass(t, Mapping):
      return Dict(allow_extra=True)
    if issubclass(t, datetime.datetime):
      return Date()
    if issubclass(t, M_Class):
      return Class(t)
    if issubclass(t, Sequence):
      return Array()

    raise Exception('unknown type "%s"' % t.__name__)

  if isinstance(t, Mapping):
    mapping = {}
    for key in t:
      mapping[key] = convert_type(t[key])
    return Dict(mapping = mapping)

  if isinstance(t, Sequence):
    l = len(t)
    if l == 0:
      return Array()
    return Array( convert_type(t[0]) )
  
  raise Exception('unknown type "%s"' % str(t))


def get_type_from_value(value):

  if isinstance(value, Mapping):
    mapping = {}
    for key in value:
      mapping[key] = get_type_from_value(value[key])
    return Dict(mapping = mapping)
  
  if not isinstance(value, string_types) and isinstance(value, Sequence):
    l = len(value)
    if l == 0:
      return Array()
    return Array( get_type_from_value(value[0]) )

  v_type = type(value)

  for it in integer_types:
    if v_type is it:
      v_type = 'number'

  return convert_type(v_type)


_type_map_ = {
    'int': Integer(),
    'integer': Integer(),
    'long': Integer(),
    'float': Number(),
    'double': Number(),
    'number': Number(),
    'str': String(),
    'string': String(),
    'unicode': String(),
    'basestring': String(),
    'bool': Boolean(),
    'boolean': Boolean(),
    'tuple': Array(),
    'list': Array(),
    'set': Array(),
    'array': Array(),
    'frozenset': Array(),
    'dict': Dict(allow_extra=True),
    'OrderedDict': Dict(allow_extra=True),
    'object': Dict(allow_extra=True),
    'datetime': Date(),
    'date': Date(),
    'NoneType': Null(),
    'null': Null(),
}


def merge_context(a, b):
  if b is None:
    return a
  if a is None:
    return b
  merged = a.copy()
  merged.update(b)
  return merged
