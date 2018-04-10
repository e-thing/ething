# coding: utf-8


from future.utils import iteritems
from .Parameter import instanciate as instanciate_parameter
from .Operation import Operation

class Path(object):
    
    
    def __init__ (self, pathname, data, parent):
        
        self.parent = parent;
        self.__pathname = pathname;
        self.data = data;
        self.__parameters = None;
        self.__operations = None
    
    
    @property
    def pathname (self):
        return self.__pathname
    
    @property
    def url (self):
        return self.parent.url + self.pathname
    
    @property
    def root (self):
        return self.parent;
    
    @property
    def parameters (self):
        
        if self.__parameters is None:
            self.__parameters = []
            
            for paramobj in self.data.get('parameters', []):
                self.__parameters.append(instanciate_parameter(paramobj, self))
            
        return self.__parameters
    
    @property
    def operations (self):
        if self.__operations is None:
            self.__operations = []
            
            for method, operationobj in iteritems(self.data):
                if method.lower() in ['get','put','post','delete','options','head','patch']:
                    self.__operations.append(Operation(method, operationobj, self))
        
        return self.__operations
    
    

