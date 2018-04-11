# coding: utf-8



from .utils import type_normalize, type_equals
from future.utils import string_types

class Field(object):
    
    
    def __init__ (self, name, type = None, compilfn = None, model_key = None):
        self._name = name
        
        if type is None or type == '*':
            self._type = '*'
        elif isinstance(type, string_types):
            self._type = [type_normalize(type)]
        else:
            self._type = [type_normalize(t) for t in type]
        
        self.__compilfn = compilfn
        self._model_key = model_key if model_key is not None else name
        
    
    @property
    def typeStr (self):
        if self._type == '*':
            return '*'
        else:
            return ','.join(self._type)
    
    @property
    def name (self):
        return self._name
    
    @property
    def model_key (self):
        return self._model_key
    
    def compil (self, operator, value):
        if callable(self.__compilfn):
            return self.__compilfn(operator, value)
        else:
            return operator.compil(self,value)
    
    def isType(self, type):
        
        if type == '*':
            return self._type == '*'
        
        if self._type == '*':
            return True
        
        for t in self._type:
            if type_equals(t, type):
                return True
        
        return False
    
    def __str__ (self):
        return self.name
    
    
    

