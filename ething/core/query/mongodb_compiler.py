# coding: utf-8

from .compiler import Compiler
from .InvalidQueryException import InvalidQueryException


def to_mongodb_type(type):
    type = type.lower()

    if type == 'string':
        return 2,
    elif type == 'boolean':
        return 8,
    elif type == 'double':
        return 1,
    elif type == 'integer':
        return 16, 18
    elif type == 'number':
        return 1, 16, 18
    elif type == 'date':
        return 9,
    elif type == 'null':
        return 10,
    elif type == 'object':
        return 3,
    elif type == 'array':
        return ()


class MongoDbCompiler (Compiler):

  def _get_model_key(self, field):
    if field == 'id':
      return '_id'
    return field
  
  def _check_type(self, exp, field, *match_type):
    if not match_type:
      return exp
    
    constraints = []

    model_key = self._get_model_key(field)

    for t in match_type:

      mts = to_mongodb_type(t)

      if mts == ():
          constraints = []
          break

      if mts is None:
          raise InvalidQueryException(
              "unknown type %s, internal error" % t)

      for mt in mts:
          constraints.append({model_key: {'$type': mt}})
    
    if len(constraints) == 1:
      return {
          '$and': [
              constraints[0],
              exp
          ]
      }
    elif len(constraints) > 1:
        return {
            '$and': [
                {
                    '$or': constraints
                },
                exp
            ]
        }

    return exp

  def _not_(self, a):
    return {
        '$nor': [a]
    }
  
  def _and_(self, a, b):
    return {
        '$and': [a, b]
    }
  
  def _or_(self, a, b):
    return {
        '$or': [a, b]
    }
  
  def _eq_(self, field, value):
    return {
      self._get_model_key(field) : value
    }
  
  def _ne_(self, field, value):
    return {
      self._get_model_key(field) : {
        '$ne': value
      }
    }
  
  def _gt_(self, field, value):
    return self._check_type({
      self._get_model_key(field) : {
        '$gt': value
      }
    }, field, 'number', 'date')
  
  def _lt_(self, field, value):
    return self._check_type({
      self._get_model_key(field) : {
        '$lt': value
      }
    }, field, 'number', 'date')
  
  def _ge_(self, field, value):
    return self._check_type({
      self._get_model_key(field) : {
        '$gte': value
      }
    }, field, 'number')
  
  def _le_(self, field, value):
    return self._check_type({
      self._get_model_key(field) : {
        '$lte': value
      }
    }, field, 'number')
  
  def _exists_(self, field):
    return {
      self._get_model_key(field): {
        '$exists': True
      }
    }
  
  def _is_(self, field, value):

    mts = to_mongodb_type(value)

    if mts is None:
        raise InvalidQueryException("unknown type '%s'" % value, self)

    constraints = []

    model_key = self._get_model_key(field)

    for mt in mts:
        constraints.append({model_key: {'$type': mt}})

    if len(constraints) == 1:
        return constraints[0]
    else:
        return {
            '$or': constraints
        }
  
  def _has_(self, field, value):
    model_key = self._get_model_key(field)

    return {
        '$or': [{
            "%s.%s" % (model_key, value): {
              '$exists': True
            }
          }, {
            model_key: value
        }]
    }
  
  def _match_(self, field, value):

    fi = value.rfind('/')
    flags = value[fi+1:]
    pattern = value[1:fi]

    return self._check_type({
      self._get_model_key(field) : {
        '$regex': pattern,
        '$options': flags
      }
    }, field, 'string')



mongodb_compiler = MongoDbCompiler()
  

