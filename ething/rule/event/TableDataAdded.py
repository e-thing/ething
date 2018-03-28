
from .ResourceEvent import ResourceEvent
from ething.TableQueryParser import TableQueryParser

class TableDataAdded(ResourceEvent):
	
	
	@staticmethod
	def validate (attributes, context):
		
		attributes.setdefault('filter', None)
		
		other = {}
		
		for key in attributes:
			
			value = attributes[key]
			
			if key == 'filter':
				
				if value is None:
					pass
				elif isinstance(value, basestring):
					
					ok, message = TableQueryParser.check(value)
					
					if not ok:
						raise Exception("invalid expression: %s" % message)
					
				else:
					raise Exception("the key '%s' must be a string" % key)
				
			else:
				other[key] = value
		
		return ResourceEvent.validate(other, context, onlyTypes=['Table'])
	
	
	@classmethod
	def emit (cls, table, data):
		return super(TableDataAdded, cls).emit(table, {
			'data' : data
		})
	
	def call(self, signal):
		
		if super(TableDataAdded, self).call(signal):
			
			if self['filter']:
				
				table = self.ething.get(signal['resource'])
				if table:
					return bool(len(table.select(length = 1, query = {
						'$and':[
							{'_id': signal['data']['id']},
							table.parser.parse(self['filter'])
						]
					})))
				
			else:
				return True
		
		return False