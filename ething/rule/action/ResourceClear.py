
from ResourceAction import ResourceAction


class ResourceClear(ResourceAction):
    
    @staticmethod
    def validate (attributes, context):
        return ResourceAction.validate(attributes, context, onlyTypes=['File','Table'])
    
    
    
    def call(self, signal):
        
        for r in self.getResourcesFromSignal(signal):
            if r.type == 'Table':
                r.clear()
            elif r.type == 'File':
                r.write('')
        
        
    
    
if __name__ == '__main__':
    
    from ething.core import Core
    from ..event import Custom
    import os
    
    name = os.path.splitext(os.path.basename(__file__))[0]
    
    rule_name = 'test-rule-%s' % name
    event_name = 'test-rule-%s-event' % name
    file_name = 'test-rule-%s-file' % name
    
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
    
    files = core.find({
        'name': file_name
    })
    
    for r in files:
        r.remove()
    
    file = core.create('File', {'name': file_name})
    file.write('test')
    
    print file.read()
    
    rule = core.createRule({
        'name' : rule_name,
        'events':[{
            'type': 'Custom',
            'options':{
                'name': event_name
            }
        }],
        'actions':[{
            'type': 'ResourceClear',
            'options':{
                'resource': file.id
            }
        }]
    })
    
    print rule
    
    signal = Custom.emit(event_name)
    
    rule.trigger(signal)
    
    assert file.read() == ''
    
    