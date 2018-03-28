from .. import Action
import time


class Sleep(Action):
	
	@staticmethod
	def validate (attributes, context):
		
		attributes.setdefault('duration', None)
		
		for key in attributes:
			
			
			if key == 'duration':
				
				duration = attributes[key]
				
				if not((isinstance(duration, int) or isinstance(duration, float)) and duration > 0 and duration < 3600 ):
					raise Exception("duration must be a number of seconds greater than 0 and lower than 1 hour.");
				
			else:
				raise Exception("%s: invalid" % key)
		
		return True
	
	
	
	def call(self, signal):
		time.sleep(self['duration'])
	


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
			'type': 'Sleep',
			'options':{
				'duration': 5
			}
		}]
	})
	
	print rule
	
	signal = Custom.emit(event_name)
	
	print "start:",time.time()
	rule.trigger(signal)
	print "end:",time.time()
	
	
	