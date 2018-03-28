

#from dateutil.parser import parse
from dateparser import parse
import datetime
from InvalidQueryException import InvalidQueryException

class Value(object):
	
	
	def __init__ (self, value = None):
		self.__value = value
	
	
	# return the intrinsec type : boolean, integer, double, string, ...
	def type (self):
		if isinstance(self.__value, bool):
			return 'boolean'
		elif isinstance(self.__value, int) or isinstance(self.__value, long):
			return 'integer'
		elif isinstance(self.__value, float):
			return 'double'
		elif isinstance(self.__value, basestring):
			return 'string'
		else:
			return 'NULL'
	
	# check if the value has the given type
	def isType(self, type):
		type = type.lower()
		
		if type == 'string' or type == 'boolean' or type == 'integer' or type == 'double':
			return self.type()==type
		elif type == 'bool':
			return self.type()=='boolean'
		elif type == 'number':
			return self.type()=='integer' or self.type()=='double'
		elif type == 'date':
			return self.type()=='string' and self.isDate()
		elif type == 'null':
			return self.type()=='NULL'
		else:
			return False
		
	
	
	def getValue (self):
		return self.__value
	
	def isDate (self):
		return bool(self.getDate())
	
	def getDate (self):
		if not hasattr(self,'__date'):
			self.__date = None
			try:
				d = parse(self.__value, languages=['en'])
				if isinstance(d, datetime.datetime):
					self.__date = d
			except:
				pass
		
		return self.__date
	
	
	def __str__ (self):
		return str(self.__value)
	



