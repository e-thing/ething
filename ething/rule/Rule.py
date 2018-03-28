

"""
 @swagger-definition
 "Rule":{ 
   "type": "object",
   "description": "

A rule object. A rule is consisted of three parts:

- The event part specifies the signal that triggers the invocation of the rule
- The condition part is a logical test that, if satisfied, causes the action to be carried out
- The action part

",
   "required":["events", "actions"],
 	 "properties":{
 		"events":{  
 		   "type":"array",
 		   "items":{
 		      "$ref": "#/definitions/Event"
 		   },
 		   "description":"A collection of events. The rule will be executed each time an event from the collection is dispatched."
 		},
 		"conditions":{  
 		   "type":"array",
 		   "items":{
 		      "$ref": "#/definitions/Condition"
 		   },
 		   "description":"A collection of conditions. May be empty."
 		},
 		"actions":{
 		   "type":"array",
 		   "items":{
 		      "$ref": "#/definitions/Action"
 		   },
 		   "description":"A collection of actions. Must not be empty !"
 		},
 		"executedDate":{  
 		   "type":"string",
 		   "format":"date-time",
 		   "description":"The last time this rule has been executed.",
         "readOnly": true
 		},
 		"executedCount":{  
 		   "type":"integer",
 		   "description":"The number of time this rule has been executed.",
         "readOnly": true
 		},
 		"createdDate":{  
 		   "type":"string",
 		   "format":"date-time",
 		   "description":"The time this rule was created.",
         "readOnly": true
 		},
 		"state":{  
 		   "type":"string",
 		   "description":"The state of this rule.",
         "readOnly": true,
         "enum": ["active", "inactive", "invalid"]
 		},
 		"enabled":{  
 		   "type":"boolean",
 		   "description":"If this rule is enabled or not."
 		},
 		"name":{  
 		   "type":"string",
 		   "description":"The name of this rule. Two or more rules can share the same name."
 		},
 		"priority":{  
 		   "type":"integer",
 		   "description":"The priority of this rule. Rules with highest priority will be executed first."
 		},
 		"repeat":{  
 		   "type":"boolean",
 		   "description":"If repeat is set to false, the actions of this rule will be executed only the first time the conditions match. Default to true."
 		}
 	 }
 }
"""


"""
 @swagger-definition
 "Event":{ 
   "type": "object",
   "description": "
The base representation of an event object used in rule.

For exemple, a rule that will be running every hour will have the following event :

```json
{
  \"type\": \"Timer\",
  \"cron\" : \"0 * * * *\"
}
```

",
   "required":["type"],
 	 "properties":{
 		"type":{  
 		   "type":"string",
 		   "description":"The type of the event."
 		}
 	 }
 }
"""

"""
 @swagger-definition
 "Condition":{ 
   "type": "object",
   "description": "
The base representation of a condition object used in rule.
",
   "required":["type"],
 	 "properties":{
 		"type":{  
 		   "type":"string",
 		   "description":"The type of the condition."
 		},
 		"isInvalid":{  
 		   "type":"boolean",
 		   "description":"Set to true if this condition is invalid.",
 		   "readOnly": true
 		}
 	 }
 }
"""

"""
 @swagger-definition
 "Action":{ 
   "type": "object",
   "description": "
The base representation of an action object used in rule.
",
   "required":["type"],
 	 "properties":{
 		"type":{  
 		   "type":"string",
 		   "description":"The type of the action."
 		},
 		"isInvalid":{  
 		   "type":"boolean",
 		   "description":"Set to true if this action is invalid.",
 		   "readOnly": true
 		}
 	 }
 }
"""



from ething.ShortId import ShortId
import datetime
import sys
import copy
from ething.Helpers import dict_recursive_update
from . import Signal
from . import Event
from . import Condition
from . import Action

from ething.meta import get_event_class, get_condition_class, get_action_class

import event
import condition
import action









class Rule(object):	
	
	
	# before calling this function, call validate(...) to check if the data are valid or not !
	def __init__ (self, ething, data):
		self.__ething = ething
		self.__d = data
		self.__events = None
		self.__conditions = None
		self.__actions = None
	
	def __str__(self):
		return 'Rule(id=%s, name=%s)' % (self.id, self.name)
	
	def __repr__(self):
		return 'Rule(id=%s, name=%s)' % (self.id, self.name)
	
	@property
	def id (self):
		return self.__d['_id']
    
	@property
	def name (self):
		return self.__d['name']
	
	@property
	def priority (self):
		return self.__d['priority']
	
	@property
	def repeat (self):
		return self.__d['repeat']
	
	@property
	def enabled (self):
		return self.__d['enabled']
	
	@property
	def createdDate (self):
		return self.__d['createdDate']
	
	@property
	def executedDate (self):
		return self.__d['executedDate']
	
	@property
	def executedCount (self):
		return self.__d['executedCount']
	
	@property
	def ething (self):
		return self.__ething
    
	@property
	def events(self):
		if self.__events is None:
			self.__events = []
			for item in self.__d['events']:
				cl = get_event_class(item['type'])
				if cl is not None:
					self.__events.append(cl(self, item))
				else:
					raise Exception("Event '%s' unknown" % item['type'])
		return self.__events
	
	@property
	def conditions(self):
		if self.__conditions is None:
			self.__conditions = []
			for item in self.__d['conditions']:
				cl = get_condition_class(item['type'])
				if cl is not None:
					self.__conditions.append(cl(self, item))
				else:
					raise Exception("Condition '%s' unknown" % item['type'])
		return self.__conditions
	
	@property
	def actions(self):
		if self.__actions is None:
			self.__actions = []
			for item in self.__d['actions']:
				cl = get_action_class(item['type'])
				if cl is not None:
					self.__actions.append(cl(self, item))
				else:
					raise Exception("Action '%s' unknown" % item['type'])
		return self.__actions
    
	
	
	def evaluate(self, signal):
		
		passed = True
		
		# tests the conditions
		index = 0
		for condition in self.conditions:
			
			test = condition.evaluate(signal)
			
			if(condition.isDirty):
				self.update()
			
			
			self.ething.log.debug("%s evaluate condition[%d] %s result:%s" % (self, index, condition, str(test)))
			
			if not test:
				passed = False
				break
			
			index += 1
		
		return passed
	
	
	def execute(self, signal):
		
		self.__d['executedDate'] = datetime.datetime.utcnow()
		self.__d['executedCount']+=1
		self.update()
		
		# execute the actions
		index = 0
		for action in self.actions:
			
			if signal.isPropagationStopped():
				self.ething.log.debug("%s signal propagation stopped" % (self))
				break
			
			self.ething.log.debug("%s executing action[%d] %s" % (self, index, action))
			
			action.execute(signal)
			
			if(action.isDirty):
				self.update()
			
			index += 1
		
	
	
	def run(self, signal = None):
		
		executed = False
		evaluated = self.evaluate(signal)
		
		lastEval = self.__d.get('_lastEval', False)
		repeat = self.__d.get('repeat', False)
		self.__d['_lastEval'] = evaluated
		
		self.ething.log.debug("rule %s triggered by signal %s eval:%s lastEval:%s repeat:%s" % (self, signal, str(evaluated), str(lastEval), str(repeat)))
		
		if not repeat and lastEval:
			evaluated = False
		
		if evaluated:
			executed = True
			self.execute(signal)
		else:
			self.update()
		
		return executed
	
	
	
	def toJson (self):
		return self.ething.r_encode(self.__d)
	
	
	
	@staticmethod
	def validate (ething, attr):
		
		context = {
			'ething' : ething
		}
		
		def validate_item (kind, index, data):
			
			if not isinstance(data, dict):
				raise Exception("Rule.%s[%d]: Must be an object." % (kind, index))
						
			data.setdefault('type', None)
			data.setdefault('options', {})
			
			
			for key in data:
				if key == 'type':
					if not isinstance(data[key], basestring) or not data[key]:
						raise Exception("Rule.%s[%d]: type must be a non empty string." % (kind, index))
				elif key == 'options':
					if data[key] is None:
						data[key] = {}
					if not isinstance(data[key], dict):
						raise Exception("Rule.%s[%d]: options must be an object." % (kind, index))
				else:
					raise Exception("Rule.%s[%d]: Unknown field '%s'." % (kind, index, key))
				
			
			
			if kind == 'event':
				col = get_event_class
			elif kind == 'condition':
				col = get_condition_class
			elif kind == 'action':
				col = get_action_class
			else:
				raise RuntimeError()
			
			cl = col(data['type'])
			if cl is None:
				raise Exception("Rule: unknown %s class '%s'" % (kind, data['type']))
			
			
			try:
				if not cl.validate(data['options'], context):
					raise Exception("Invalid atributes.")
			
			except:
				raise Exception("Rule.%s[%d]: %s" % (kind, index, sys.exc_info()[1]))
			
			data['error'] = False
			data['isInvalid'] = False
		
		
		attr.setdefault('name', '')
		attr.setdefault('priority', 0)
		attr.setdefault('repeat', True)
		attr.setdefault('events', [])
		attr.setdefault('conditions', [])
		attr.setdefault('actions', [])
		
		for key in attr:
			if key == 'name':
				if not isinstance(attr[key], basestring) or not attr[key]:
					raise Exception("Rule: Invalid field '%s'. Must be a non empty string." % (key))
			elif key == 'enabled' or key == 'repeat':
				if not isinstance(attr[key], bool):
					raise Exception("Rule: Invalid field '%s'. Must be a boolean." % (key))
			elif key == 'priority':
				if not isinstance(attr[key], int):
					raise Exception("Rule: Invalid field '%s'. Must be an integer." % (key))
			elif key == 'actions' or key == 'events' or key == 'conditions':
				if not isinstance(attr[key], list):
					raise Exception("Rule: Invalid field '%s'. Must be an array." % (key))
				if key == 'actions' or key == 'events':
					if len(attr[key])==0:
						raise Exception("Rule: no %s." % (key))
				index = 0
				for item in attr[key]:
					validate_item(key[:-1], index, item)
					index += 1
			else:
				raise Exception("Rule: Unknown field '%s'." % (key))
		
		
		return True
	
	
	@staticmethod
	def create (ething, attr):
		
		attr = copy.deepcopy(attr)
		
		Rule.validate(ething, attr)
		
		c = ething.db["rules"]
		
		attr.update({
			'_id' : ShortId.generate(),
			'createdDate' : datetime.datetime.utcnow(),
			'executedDate' : None,
			'executedCount' : 0,
			'enabled' : True
		})
		
		try:
			c.insert_one(attr)
		except:
			raise Exception('db error: %s' % (sys.exc_info()[1]))
		
		
		rule = Rule(ething, attr)
		
		ething.log.debug("Rule created : %s" % str(rule))
		
		return rule
	
	
	
	def remove (self):
		c = self.ething.db["rules"]
		
		c.delete_one({'_id' : self.id})
		
		self.ething.log.debug("Rule deleted : %s" % str(self))
		
		self.__d = None
		self.__events = None
		self.__conditions = None
		self.__actions = None
	
	
	def set (self, attr):
		
		attr = dict_recursive_update({}, self.__d, attr)
		
		self.validate(self.ething, attr)
		
		self.__d = attr
		
		self.update()
		
		self.__events = None
		self.__conditions = None
		self.__actions = None
		
		return True
	
	
	def update (self):
		c = self.ething.db["rules"]
		c.replace_one({'_id' : self.id}, self.__d)
	
	
	def trigger (self, signal):
		if self.enabled:
			for event in self.events:
				if signal.name == event.type:
					
					passed = False
					try:
						passed = event.match(signal)
					except Exception as e:
						self.ething.log.error(e)
					
					if(passed):
						self.run(signal)
						return True
				
			
		
		return False
	
	
	
if __name__ == '__main__':
	
	from ething.core import Core
	
	ething = Core({
		'db':{
			'database': 'test'
		},
		'log':{
			'level': 'debug'
		}
	})
	
	#rule = ething.createRule({
	#	'name' : 'myrule',
	#	'events':[{
	#		'type': 'Custom',
	#		'options':{
	#			'name': 'toto'
	#		}
	#	}],
	#	'actions':[{
	#		'type': 'Sleep',
	#		'options':{
	#			'duration': 1
	#		}
	#	}]
	#})
	
	from .event import Custom
	
	signal = Custom.emit('toto')
	
	ething.dispatchSignal(signal, False)
	
	#print ething.findRules()[0]




