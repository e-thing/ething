# coding: utf-8

from .compiler import Compiler
from .InvalidQueryException import InvalidQueryException
from future.utils import string_types, integer_types
from collections import Iterable, Mapping
import datetime
import re


number_types = integer_types + (float, )

none_type = type(None)

type_map = {
  'boolean': bool,
  'integer': integer_types,
  'double': float,
  'string': string_types,
  'array': Iterable,
  'object': Mapping,
  'null': none_type,
  'number': number_types,
  'date': datetime.datetime
}

class AttributeCompiler (Compiler):

  def _cast_value_(self, field, value):
    return value
  
  def _check_field(self, obj, field, *match_type):

    attr_exists = True
    attr_value = None

    parts = field.split('.')
    attr_value = obj
    for a in parts:
      if isinstance(attr_value, Mapping) and a in attr_value:
        attr_value = attr_value[a]
      elif hasattr(attr_value, a):
        attr_value = getattr(attr_value, a)
      else:
        attr_exists = False
        break

    if attr_exists:

      attr_value = self._cast_value_(field, attr_value)

      if not match_type:
        return True, attr_value
      
      # check that the value has the right type !
      types = set()
      for t in match_type:
        mt = type_map[t]
        if isinstance(mt, tuple):
          types = types.union(mt)
        else:
          types.add(mt)
      return isinstance(attr_value, tuple(types)), attr_value
    
    return False, None

  def _wrap(self, field, test, *match_type):
    def wrapper(obj):
      res, value = self._check_field(obj, field, *match_type)
      if res:
        return test(value)
      else:
        return False
    return wrapper

  def _not_(self, a):
    return lambda obj: not a(obj)
  
  def _and_(self, a, b):
    return lambda obj: a(obj) and b(obj)
  
  def _or_(self, a, b):
    return lambda obj: a(obj) or b(obj)
  
  def _eq_(self, field, value):
    return self._wrap(field, lambda v: v == value)
  
  def _ne_(self, field, value):
    return self._wrap(field, lambda v: v != value)
  
  def _gt_(self, field, value):
    return self._wrap(field, lambda v: v > value, 'number', 'date')
  
  def _lt_(self, field, value):
    return self._wrap(field, lambda v: v < value, 'number', 'date')
  
  def _ge_(self, field, value):
    return self._wrap(field, lambda v: v >= value, 'number')
  
  def _le_(self, field, value):
    return self._wrap(field, lambda v: v <= value, 'number')

  def _exists_(self, field):
    def test(obj):
      res, _ = self._check_field(obj, field)
      return res
    
    return test
  
  def _is_(self, field, value):

    if value not in type_map:
      raise InvalidQueryException('unknown type %s' % value)
    
    def test(obj):
      res, _ = self._check_field(obj, field, value)
      return res
    
    return test
  
  def _has_(self, field, value):
    def test(obj):
      res, v = self._check_field(obj, field, 'array', 'object')
      if res:
        return value in v
      return False
    
    return test
  
  def _match_(self, field, value):

    fi = value.rfind('/')
    flags = value[fi+1:]
    pattern = value[1:fi]

    flags_value = 0
    for fl in flags.upper():
      flag_v = getattr(re, fl, None)
      if flag_v is not None:
        flags_value = flags_value | flag_v
    
    re_exp = re.compile(pattern, flags_value)

    return self._wrap(field, lambda v: bool(re_exp.search(v)), 'string')


attribute_compiler = AttributeCompiler()
