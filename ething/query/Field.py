




class Field(object):
	
	
	def __init__ (self, name, type = None, compilfn = None):
		self._name = name
		self._type = type if type else '*'
		self.__compilfn = compilfn
		
	
	@property
	def type (self):
		return self._type
	
	@property
	def name (self):
		return self._name
	
	def compil (self, operator, value):
		if callable(self.__compilfn):
			return self.__compilfn(operator, value)
		else:
			return operator.compil(self,value)
	
	
	def __str__ (self):
		return self.name
	


