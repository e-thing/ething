# coding: utf-8
from future.utils import string_types
from .utils import type_normalize, type_equals
from .InvalidQueryException import InvalidQueryException

class Operator(object):
    
    def __init__ (self, syntax, compilfn, accept = None, acceptValue = None):
        
        self.syntax = syntax
        
        if accept is None or accept == '*':
            accept = '*'
        elif isinstance(accept, string_types):
            accept = [type_normalize(accept)]
        else:
            accept = [type_normalize(t) for t in accept]
        
        if acceptValue is None:
            acceptValue = accept
        elif acceptValue is False or acceptValue == '*':
            pass
        elif isinstance(acceptValue, string_types):
            acceptValue = [type_normalize(acceptValue)]
        else:
            acceptValue = [type_normalize(t) for t in acceptValue]
        
        self.__acceptField = accept
        self.__acceptValue = acceptValue
        
        self.compilfn = compilfn
        
    
    
    def accept (self, field, value):
        
        if not self.acceptField(field):
            raise InvalidQueryException("the operator '%s' is not compatible with the field '%s'[type=%s]" % (self, field, field.typeStr))
        
        if not self.acceptValue(value):
            raise InvalidQueryException("the operator '%s' is not compatible with the given value" % (self))
        
        return True
    
    
    def acceptField (self, field):
        if self.__acceptField == '*':
            return True
        
        for t in self.__acceptField:
            if field.isType(t):
                return True
        
        return False
    
    
    def acceptValue (self, value):
        
        if self.__acceptValue == '*':
            return True
        
        if not self.hasValue():
            return value is None
        
        for type in self.__acceptValue:
            if value.isType(type):
                return True
        
        return False
    
    
    def hasValue (self):
        return self.__acceptValue is not False
    
    
    def compil (self, field, value):
        
        constraints = []
        
        field_key = field.model_key
        
        # type constraints (indeed, certains operators must only be applied on field with specific type
        # is it necessary ?
        if isinstance(self.__acceptField, list):
            for type in self.__acceptField:
                
                mts = to_mongodb_type(type)
                
                if mts == ():
                    constraints = []
                    break
                
                if mts is None:
                    raise InvalidQueryException("unknown type %s, internal error" % (type))
                
                for mt in mts:
                    constraints.append( { field_key : { '$type' : mt } } )
                    
        
        compiled = self.compilfn(field, value)
        
        if len(constraints)==1:
            return {
                '$and': [
                    constraints[0],
                    compiled
                ]
            }
        elif len(constraints)>1:
            return {
                '$and': [
                    {
                        '$or': constraints
                    },
                    compiled
                ]
            }
        
        return compiled
        
    
    
    def __str__ (self):
        return self.syntax
    



def to_mongodb_type(type):
    type = type.lower()
    
    if type == 'string':
        return (2,)
    elif type == 'boolean':
        return (8,)
    elif type == 'double':
        return (1,)
    elif type == 'integer':
        return (16, 18)
    elif type == 'number':
        return (1, 16, 18)
    elif type == 'date':
        return (9,)
    elif type == 'null':
        return (10,)
    elif type == 'object':
        return (3,)
    elif type == 'array':
        return ()

    




# default operators



class EqualOperator(Operator):
    
    def __init__ (self):
        super(EqualOperator, self).__init__('==', self.__compil)
    
    def __compil(self,field,value):
        
        if value.isType('date'):
            v = value.getDate()
        else:
            v = value.getValue()
        
        return {
            field.model_key : v
        }

class NotEqualOperator(Operator):
    
    def __init__ (self):
        super(NotEqualOperator, self).__init__('!=', self.__compil)
    
    def __compil(self,field,value):
        
        if value.isType('date'):
            v = value.getDate()
        else:
            v = value.getValue()
        
        return {
            field.model_key : {
                '$ne': v
            }
        }
    
class ExistOperator(Operator):
    
    def __init__ (self):
        super(ExistOperator, self).__init__('exists', self.__compil, '*', False)
    
    def __compil(self,field,value):
        return {
            field.model_key : {
                '$exists': True
            }
        }

class IsOperator(Operator):
    
    def __init__ (self):
        super(IsOperator, self).__init__('is', self.__compil, '*', 'string')
    
    def __compil(self,field,value):
        
        type = value.getValue()
        
        mts = to_mongodb_type(type)
        
        if mts is None:
            raise InvalidQueryException("unknown type '%s'" % type,self)
        
        constraints = []
        
        for mt in mts:
            constraints.append( { field.model_key : { '$type' : mt } } )
        
        if len(constraints) == 1:
            return constraints[0]
        else:
            return {
                '$or': constraints
            }
        

class LowerOperator(Operator):
    
    def __init__ (self):
        super(LowerOperator, self).__init__('<', self.__compil, ['integer','double','date'])
    
    def __compil(self,field,value):
        if value.isType('date'):
            v = value.getDate()
        else:
            v = value.getValue()
        return {
            field.model_key : {
                '$lt': v
            }
        }

class GreaterOperator(Operator):
    
    def __init__ (self):
        super(GreaterOperator, self).__init__('>', self.__compil, ['integer','double','date'])
    
    def __compil(self,field,value):
        if value.isType('date'):
            v = value.getDate()
        else:
            v = value.getValue()
        return {
            field.model_key : {
                '$gt': v
            }
        }

class LowerOrEqualOperator(Operator):
    
    def __init__ (self):
        super(LowerOrEqualOperator, self).__init__('<=', self.__compil, ['integer','double'])
    
    def __compil(self,field,value):
        return {
            field.model_key : {
                '$lte': value.getValue()
            }
        }

class GreaterOrEqualOperator(Operator):
    
    def __init__ (self):
        super(GreaterOrEqualOperator, self).__init__('>=', self.__compil, ['integer','double'])
    
    def __compil(self,field,value):
        return {
            field.model_key : {
                '$gte': value.getValue()
            }
        }

class StartWithOperator(Operator):
    
    def __init__ (self):
        super(StartWithOperator, self).__init__('^=', self.__compil, ['string'])
    
    def __compil(self,field,value):
        return {
            field.model_key : {
                '$regex': '^'+value.getValue()
            }
        }
class EndWithOperator(Operator):
    
    def __init__ (self):
        super(EndWithOperator, self).__init__('$=', self.__compil, ['string'])
    
    def __compil(self,field,value):
        return {
            field.model_key : {
                '$regex': value.getValue()+'$'
            }
        }
class ContainOperator(Operator):
    
    def __init__ (self):
        super(ContainOperator, self).__init__('*=', self.__compil, ['string'])
    
    def __compil(self,field,value):
        return {
            field.model_key : {
                '$regex': value.getValue()
            }
        }
class ContainWordOperator(Operator):
    
    def __init__ (self):
        super(ContainWordOperator, self).__init__('~=', self.__compil, ['string'])
    
    def __compil(self,field,value):
        return {
            field.model_key : {
                '$regex': '(^|\s)'+value.getValue()+'($|\s)'
            }
        }

class HasOperator(Operator):
    
    def __init__ (self):
        super(HasOperator, self).__init__('has', self.__compil, ['object', 'array'], 'string')
    
    def __compil(self,field,value):
        
        if field.isType('*'):
            return {
                '$or': [{
                        "%s.%s" % (field.model_key,value.getValue()) : {
                            '$exists': True
                        }
                    },{
                        field.model_key : value.getValue()
                    }]
            }
        elif field.isType('object'):
            return {
                "%s.%s" % (field.model_key,value.getValue()) : {
                    '$exists': True
                }
            }
        else:
            return {
                field.model_key : value.getValue()
            }

