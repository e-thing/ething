
from InvalidQueryException import InvalidQueryException

class Operator(object):
	
	def __init__ (self, syntax, compilfn, accept = None, acceptValue = None):
		
		self.syntax = syntax
		
		if accept is None:
			accept = '*'
		if acceptValue is None:
			acceptValue = accept
		
		self.__acceptField = accept
		self.__acceptValue = acceptValue
		if isinstance(self.__acceptField, basestring) and self.__acceptField != '*':
			self.__acceptField = [self.__acceptField]
		if isinstance(self.__acceptValue, basestring) and self.__acceptValue != '*':
			self.__acceptValue = [self.__acceptValue]
		
		self.compilfn = compilfn
		
	
	
	def accept (self, field, value):
		if not self.acceptField(field):
			raise InvalidQueryException("the operator '%s' is not compatible with the field '%s'[type=%s]" % (self, field, field.type))
		
		if not self.acceptValue(value):
			raise InvalidQueryException("the operator '%s' is not compatible with the given value" % (self))
		
		return True
	
	
	def acceptField (self, field):
		if isinstance(self.__acceptField, basestring) and self.__acceptField == '*':
			return True
		ft = field.type
		if isinstance(ft, basestring) and ft == '*':
			return True
		if isinstance(self.__acceptField, list) and ft in self.__acceptField:
			return True
		return False
	
	
	def acceptValue (self, value):
		if isinstance(self.__acceptValue, basestring) and self.__acceptValue == '*':
			return True
		
		if not self.hasValue():
			return False
		
		if isinstance(self.__acceptValue, list):
			for type in self.__acceptValue:
				if value.isType(type):
					return True
		
		return False
	
	
	def hasValue (self):
		return not(isinstance(self.__acceptValue, bool) and self.__acceptValue == False)
	
	
	def compil (self, field, value):
		
		constraints = []
		
		# type constraints (indeed, certains operators must only be applied on field with specific type
		# is it necessary ?
		if isinstance(self.__acceptField, list):
			for type in self.__acceptField:
				if type == 'string':
					constraints.append( { str(field) : { '$type' : 2 } } )
				elif type == 'bool' or type == 'boolean':
					constraints.append( { str(field) : { '$type' : 8 } } )
				elif type == 'double':
					constraints.append( { str(field) : { '$type' : 1 } } )
				elif type == 'integer':
					constraints.append( { str(field) : { '$type' : 16 } } )
					constraints.append( { str(field) : { '$type' : 18 } } )
				elif type == 'number':
					constraints.append( { str(field) : { '$type' : 1 } } )
					constraints.append( { str(field) : { '$type' : 16 } } )
					constraints.append( { str(field) : { '$type' : 18 } } )
				elif type == 'date':
					constraints.append( { str(field) : { '$type' : 9 } } )
				else:
					raise InvalidQueryException("unknown type %s, internal error" % (type)); # internal error
		
		compiled = self.compilfn(field, value)
		
		if len(constraints)==1:
			return {
				'$and': [
					constraints[0],
					compiled
				]
			}
		elif len(constraints)>1:
			return {
				'$and': [
					{
						'$or': constraints
					},
					compiled
				]
			}
		
		return compiled
		
	
	
	def __str__ (self):
		return self.syntax
	

# default operators



class EqualOperator(Operator):
	
	def __init__ (self):
		super(EqualOperator, self).__init__('==', self.__compil)
	
	def __compil(self,field,value):
		
		if value.isType('date'):
			v = value.getDate()
		else:
			v = value.getValue()
		
		return {
			str(field) : v
		}

class NotEqualOperator(Operator):
	
	def __init__ (self):
		super(NotEqualOperator, self).__init__('!=', self.__compil)
	
	def __compil(self,field,value):
		
		if value.isType('date'):
			v = value.getDate()
		else:
			v = value.getValue()
		
		return {
			str(field) : {
				'$ne': v
			}
		}
	
class ExistOperator(Operator):
	
	def __init__ (self):
		super(ExistOperator, self).__init__('exists', self.__compil, '*', False)
	
	def __compil(self,field,value):
		return {
			str(field) : {
				'$exists': True
			}
		}

class IsOperator(Operator):
	
	def __init__ (self):
		super(IsOperator, self).__init__('is', self.__compil, '*', 'string')
	
	def __compil(self,field,value):
		
		type = value.getValue().lower()
		
		if type == 'string':
			return {
				str(field) : {
					'$type': 2
				}
			}
		elif type == 'boolean' or type == 'bool':
			return {
				str(field) : {
					'$type': 8
				}
			}
		elif type == 'number':
			return {
				'$or': [
					{
						str(field) : {
							'$type': 1
						}
					},
					{
						str(field) : {
							'$type': 16
						}
					},
					{
						str(field) : {
							'$type': 18
						}
					}
				]
			}
		elif type == 'integer':
			return {
				'$or': [
					{
						str(field) : {
							'$type': 16
						}
					},
					{
						str(field) : {
							'$type': 18
						}
					}
				]
			}
		elif type == 'float' or type == 'double':
			return {
				str(field) : {
					'$type': 1
				}
			}
		elif type == 'null':
			return {
				str(field) : {
					'$type': 10
				}
			}
		else:
			raise InvalidQueryException("unknown type '%s'" % type,self)
		

class LowerOperator(Operator):
	
	def __init__ (self):
		super(LowerOperator, self).__init__('<', self.__compil, ['integer','double','date'])
	
	def __compil(self,field,value):
		if value.isType('date'):
			v = value.getDate()
		else:
			v = value.getValue()
		return {
			str(field) : {
				'$lt': v
			}
		}

class GreaterOperator(Operator):
	
	def __init__ (self):
		super(GreaterOperator, self).__init__('>', self.__compil, ['integer','double','date'])
	
	def __compil(self,field,value):
		if value.isType('date'):
			v = value.getDate()
		else:
			v = value.getValue()
		return {
			str(field) : {
				'$gt': v
			}
		}

class LowerOrEqualOperator(Operator):
	
	def __init__ (self):
		super(LowerOrEqualOperator, self).__init__('<=', self.__compil, ['integer','double'])
	
	def __compil(self,field,value):
		return {
			str(field) : {
				'$lte': value.getValue()
			}
		}

class GreaterOrEqualOperator(Operator):
	
	def __init__ (self):
		super(GreaterOrEqualOperator, self).__init__('>=', self.__compil, ['integer','double'])
	
	def __compil(self,field,value):
		return {
			str(field) : {
				'$gte': value.getValue()
			}
		}

class StartWithOperator(Operator):
	
	def __init__ (self):
		super(StartWithOperator, self).__init__('^=', self.__compil, ['string'])
	
	def __compil(self,field,value):
		return {
			str(field) : {
				'$regex': '^'+value.getValue()
			}
		}
class EndWithOperator(Operator):
	
	def __init__ (self):
		super(EndWithOperator, self).__init__('$=', self.__compil, ['string'])
	
	def __compil(self,field,value):
		return {
			str(field) : {
				'$regex': value.getValue()+'$'
			}
		}
class ContainOperator(Operator):
	
	def __init__ (self):
		super(ContainOperator, self).__init__('*=', self.__compil, ['string'])
	
	def __compil(self,field,value):
		return {
			str(field) : {
				'$regex': value.getValue()
			}
		}
class ContainWordOperator(Operator):
	
	def __init__ (self):
		super(ContainWordOperator, self).__init__('~=', self.__compil, ['string'])
	
	def __compil(self,field,value):
		return {
			str(field) : {
				'$regex': '(^|\s)'+value.getValue()+'($|\s)'
			}
		}



