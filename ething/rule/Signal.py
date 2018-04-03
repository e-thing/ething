
import time

class Signal(object):
    
    
    def __init__ (self, name, attributes = {}):
        super(Signal, self).__setattr__('_Signal__name', name)
        super(Signal, self).__setattr__('_Signal__d', attributes)
        super(Signal, self).__setattr__('_Signal__ts', time.time())
        super(Signal, self).__setattr__('_Signal__propagationStopped', False)
    
    @property
    def name (self):
        return self.__name
    
    @property
    def timestamp (self):
        return self.__ts
    
    
    def __getitem__ (self, name):
        return self.__d.get(name, None)
    
    def __setitem__ (self, name, value):
        self.__d[name] = value
    
    def __delitem__ (self, name):
        if self.__d.has_key(name):
            del self.__d[name]
    
    def __str__(self):
        return 'Signal(name=%s, %s)' % (self.name, str(self.__d))
    
    def __repr__(self):
        return 'Signal(name=%s, %s)' % (self.name, str(self.__d))
    
    
    def stopPropagation (self):
        self.__propagationStopped = True
    
    
    def isPropagationStopped (self):
        return self.__propagationStopped
    
    
    def toJson (self):
        return {
            'name' : self.__name,
            'ts' : self.__ts,
            'data' : self.__d
        }