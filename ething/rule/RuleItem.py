
class RuleItem(object):

    
    def __init__ (self, rule, attributes = {}):
        self.__isDirty = False
        self.__d = attributes
        self.__rule = rule
    
    def __getitem__ (self, name):
        return self.__d.get('options',{}).get(name, None)
    
    def __setitem__ (self, name, value):
        self.__d.setdefault('options',{})[name] = value
        self.__isDirty = True
    
    def __delitem__ (self, name):
        if self.__d.has_key('options') and self.__d['options'].has_key(name):
            del self.__d['options'][name]
            self.__isDirty = True
    
    def __str__(self):
        return '%s()' % (self.type)
    
    def __repr__(self):
        return '%s()' % (self.id)
    
    @property
    def type (self):
        return self.__d['type']
    
    @property
    def rule (self):
        return self.__rule
    
    @property
    def ething (self):
        return self.__rule.ething
    
    @property
    def valid (self):
        return not self.__d.get('isInvalid', False)
    
    @valid.setter
    def valid(self, value):
        self.__d['isInvalid'] = not bool(value)
        self.__isDirty = True
    
    @property
    def error (self):
        return self.__d.get('error', None)
    
    @error.setter
    def error(self, value):
        if isinstance(value, basestring):
            error = value if value else 'unspecified error'
        elif isinstance(value, Exception):
            error = repr(value)
        elif value is None or (isinstance(value, bool) and not value):
            error = None
        else:
            error = 'unknown error'
        
        if self.__d.get('error', None) != error:
            self.__d['error'] = error
            self.__isDirty = True
    
    @property
    def isDirty (self):
        return self.__isDirty
    
    
    def toJson (self):
        return self.__d
    
    
    # attributes validation function
    @staticmethod
    def validate (attributes, context):
        return len(attributes) == 0 # default implementation
