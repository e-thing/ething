# coding: utf-8
from future.utils import string_types
from .. import Action
from .. import InvalidRuleException
from ething.ScriptEngine import ScriptEngine



class ScriptExecution(Action):
    
    @staticmethod
    def validate (attributes, context):
        
        attributes.setdefault('script', None)
        attributes.setdefault('arguments', None)
        
        for key in attributes:
            
            value = attributes[key]
            
            if key == 'script':
                
                if not( isinstance(value, string_types) and len(value)>0 ):
                    raise Exception("%s: must be a resource id." % key)
                
                script = context['ething'].get(value)
                if not script:
                    raise Exception("%s: no resource found with id = %s." % (key, value))
                
                if not script.isTypeof('File') or script.mime != 'application/javascript':
                    raise Exception("%s: the file %s is not a script" % (key, str(script)))
                
            elif key == 'arguments':
                
                if value is not None:
                    if not( isinstance(value, string_types) and len(value)>0 ):
                        raise Exception("%s: must be a non empty string" % key)
            
            else:
                raise Exception("%s: invalid" % key)
        
        return True
    
    
    
    def call(self, signal):
        
        script = self.ething.get(self['script'])
        if not script:
            raise InvalidRuleException("unable to find the resource with id '%s'" % self['script'])
        
        result = ScriptEngine.runFromFile(script, self['arguments'])
        
        if not result['ok']:
            raise Exception('the script returned with return_code = %d' % result['return_code'] )
        
        
    
    
