from .. import Action



class Log(Action):
	
	@staticmethod
	def validate (attributes, context):
		
		attributes.setdefault('message', None)
		
		for key in attributes:
			
			value = attributes[key]
			
			if key == 'message':
				
				if not( isinstance(value, basestring) and len(value)>0 ):
					raise Exception("%s: must be a non empty string." % key)
			
			else:
				raise Exception("%s: invalid" % key)
		
		return True
	
	
	
	def call(self, signal):
		self.ething.log.info(self['message'])
	
	

if __name__ == '__main__':
	
	from ething.core import Core
	from ..event import Custom
	import os
	
	name = os.path.splitext(os.path.basename(__file__))[0]
	
	rule_name = 'test-rule-%s' % name
	event_name = 'test-rule-%s-event' % name
	
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
	
	rule = core.createRule({
		'name' : rule_name,
		'events':[{
			'type': 'Custom',
			'options':{
				'name': event_name
			}
		}],
		'actions':[{
			'type': 'Log',
			'options':{
				'message': "hello world"
			}
		}]
	})
	
	print rule
	
	signal = Custom.emit(event_name)
	
	rule.trigger(signal)
	
	
	