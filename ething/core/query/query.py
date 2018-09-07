# coding: utf-8

from .Stream import Stream
import unicodedata
import re
import sys
from .Field import Field
from .Value import Value
from .Operator import *
from .InvalidQueryException import InvalidQueryException


class Query(object):

  operators = {
      '==': EqualOperator(),
      '!=': NotEqualOperator(),
      'exists': ExistOperator(),
      'is': IsOperator(),
      '<': LowerOperator(),
      '>': GreaterOperator(),
      '<=': LowerOrEqualOperator(),
      '>=': GreaterOrEqualOperator(),
      'has': HasOperator(),
      'match': MatchOperator(),
  }

  def __init__(self, compiler, constants = None, fields = None, allow_unknown_fields = True, tz = None):
    self.compiler = compiler
    self.constants = constants or dict()
    self.fields = fields or dict()
    self.allow_unknown_fields = allow_unknown_fields
    self.tz = tz or 'UTC'

  
  def compile(self, expression):
    stream = Stream(expression)
    return self._compileExpression(stream)
  
  def check(self, expression):
    message = ''
    ok = True
    try:
        self.compile(expression)
    except:
        ok = False
        message = sys.exc_info()[1]

    return ok, message

  def _compileExpression(self, stream):

    stack = []

    stream.skipSpace()

    if not stream.length():
        raise InvalidQueryException('empty expression', stream)

    # get the first fragment
    stack.append(self._compileFragment(stream))

    # search for other FOV expressions separated by a logical operator
    while stream.length() > 0 and not stream.match('\)'):

        # search for a logical operator
        logic = stream.read('(and|or)($|\s+)', True)
        if logic:
            stack.append(logic.strip().lower())
        else:
            raise InvalidQueryException(
                'waiting for a logical operator', stream)

        # search for a fragment
        stack.append(self._compileFragment(stream))

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
                exp = getattr(self.compiler, '_%s_' % currentLogic)(stack[i-1], stack[i+1])

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
  
  def _compileFragment(self, stream):
    """
    Parse a FOV or a enclosed expression optionnaly preceded by not operator
    """
    stream.skipSpace()

    if stream.read('not($|\s+)', True):
          return self.compiler._not_(self._compileFragment(stream))
    
    if not stream.length():
        raise InvalidQueryException('waiting an expression', stream)

    if stream.read('\('):
        # start enclosure
        f = self._compileExpression(stream)

        # must be followed by a ')'
        stream.skipSpace()

        if not stream.read('\)'):
            raise InvalidQueryException("expected a ')'", stream)

    else:
        f = self._compileFOV(stream)
    
    stream.skipSpace()

    return f
  
  def _compileFOV(self, stream):
      """
      parse a Field-Operator-Value expression
      """

      field = self._parseField(stream)
      op, op_syntax = self._parseOperator(stream)
      value = self._parseValue(stream) if op.hasValue() else None

      try:
        if not op.accept(field, value):
            raise Exception("unknown")
      except:
          raise InvalidQueryException("operator '%s' : %s" % (op_syntax, sys.exc_info()[1]), stream)
      
      casted_field = str(field)

      arg = [casted_field]
      if op.hasValue():
        casted_value = op.cast_value(value)
        arg.append(casted_value)
      
      try:
          compiled = getattr(self.compiler, '_%s_' % op.name)(*arg)
      except:
          raise InvalidQueryException(sys.exc_info()[1], stream)

      return compiled

  def _parseField(self, stream):
      stream.skipSpace()

      field = stream.read('[a-zA-Z0-9\.\-_]+')
      if field:
          if field in self.fields:
              f = self.fields[field]
              if isinstance(f, string_types):
                f = Field(field, f)
              return f
          else:
            
              if self.allow_unknown_fields:
                return Field(field)
              else:
                raise InvalidQueryException(
                  "unknown field '%s'" % field, stream)
      else:
          raise InvalidQueryException('expected a field', stream)

  def _parseOperator(self, stream):
      stream.skipSpace()

      op = stream.read('[^a-zA-Z0-9\.\-_\(\)\s]+')
      if not op:
          op = stream.readWord()
      if op:
          if op in self.operators:
              return self.operators[op], op
          else:
              raise InvalidQueryException(
                  "unknown operator '%s'" % op, stream)
      else:
          raise InvalidQueryException("expected an operator", stream)

  def _parseValue(self, stream):
      stream.skipSpace()

      v = stream.read(r'"(?:\\.|[^"\\])*"')
      if not v:
          v = stream.read(r"'(?:\\.|[^'\\])*'")
      # try to get string (double quotes or simple quotes)
      if v:
          # quoted string
          return Value(self, v[1:-1])

          # r = v[1:-1] # remove the quotes
          # if(v[0] == '"'):
          #    r = r.decode('string_escape')
          #
          # return Value(self, r)

      else:
          v = stream.read('[a-zA-Z0-9\.\-_+]+')

          if v:
            # number ? (integer or float)
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

            # null ?
            m = re.search('^null$', v, re.IGNORECASE)
            if m:
                return Value(self, None)

            # maybe a CONSTANT
            if v in self.constants:
                return Value(self, self.constants[v])
            
            raise InvalidQueryException("invalid value '%s'" % v, stream)
          
          else:
            # regular expression
            pattern = stream.read(r'/(?:\\.|[^/\\])*/([a-zA-Z]+)?')
            if pattern:
              return Value(self, pattern, 'regex')

          raise InvalidQueryException("missing a value", stream)


  
