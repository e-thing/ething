from .ResourceCondition import ResourceCondition
from ething.ResourceQueryParser import ResourceQueryParser


class ResourceMatch(ResourceCondition):
	
	@staticmethod
	def validate (attributes, context):
		
		attributes.setdefault('expression', None)
		
		other = {}
		
		for key in attributes:
			
				
			if key == 'expression':
				
				expr = attributes[key]
				
				if not( isinstance(expr, basestring) and len(expr)>0 ):
					raise Exception("must be a non empty string.")
				
				ok, message = ResourceQueryParser.check(value)
				
				if not ok:
					raise Exception("invalid expression: %s" % message)
				
				
			else:
				other[key] = attributes[key]
		
		return ResourceCondition.validate(other, context)
	
	
	
	def call(self, signal):
		
		resources = self.getResourcesFromSignal(signal)
		
		for r in resources:
			if not r.match(self['expression']):
				return False
		
		return True
	