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
                
                if not( isinstance(value, basestring) and len(value)>0 ):
                    raise Exception("%s: must be a resource id." % key)
                
                script = context['ething'].get(value)
                if not script:
                    raise Exception("%s: no resource found with id = %s." % (key, value))
                
                if not script.isTypeof('File') or script.mime != 'application/javascript':
                    raise Exception("%s: the file %s is not a script" % (key, str(script)))
                
            elif key == 'arguments':
                
                if value is not None:
                    if not( isinstance(value, basestring) and len(value)>0 ):
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
        
        
    
    

if __name__ == '__main__':
    
    from ething.core import Core
    from ..event import Custom
    import os
    
    name = os.path.splitext(os.path.basename(__file__))[0]
    
    rule_name = 'test-rule-%s' % name
    event_name = 'test-rule-%s-event' % name
    script_name = 'test-rule-%s-script.js' % name
    
    core = Core({
        'db':{
            'database': 'test'
        },
        'log':{
            'level': 'debug'
        }
    })
    
    rules = core.findRules({
        'name' : rule_name
    })
    
    for r in rules:
        r.remove()
    
    scripts = core.find({
        'name': script_name
    })
    
    for r in scripts:
        r.remove()
    
    script = core.create('File', { 'name': script_name })
    script.write('console.log("hello world");')
    
    print script.mime
    
    rule = core.createRule({
        'name' : rule_name,
        'events':[{
            'type': 'Custom',
            'options':{
                'name': event_name
            }
        }],
        'actions':[{
            'type': 'ScriptExecution',
            'options':{
                'script': script.id
            }
        }]
    })
    
    print rule
    
    signal = Custom.emit(event_name)
    
    rule.trigger(signal)
    
    
    