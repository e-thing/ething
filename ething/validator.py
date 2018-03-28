
import re
import sys


class Validator(object):
	
	def validate(self, value):
		raise NotImplemented()
	
	def __or__(self, other):
		return Or(self, other)
	
	def __and__(self, other):
		return And(self, other)

class Or(Validator):
	
	def __init__(self, *args):
		self.items = args
	
	def validate(self, value):
		error = None
		for i in self.items:
			try:
				i.validate(value)
				return
			except Exception as e:
				if error is None:
					error = e
		
		raise e

class And(Validator):
	
	def __init__(self, *args):
		self.items = args
	
	def validate(self, value):
		for i in self.items:
			i.validate(value)


class isAnything(Validator):
	
	def validate(self, value):
		pass

class isNone(Validator):
	
	def validate(self, value):
		if value is not None:
			raise ValueError('not None')


class isNumber(Validator):
	
	def __init__(self, min = None, max = None):
		self.min = min
		self.max = max
	
	def validate(self, value):
		if not isinstance(value, int) and not isinstance(value, float):
			raise ValueError('not a number')
		if self.min is not None:
			if value < self.min:
				raise ValueError('value < %s', str(self.min))
		if self.max is not None:
			if value > self.max:
				raise ValueError('value > %s', str(self.max))

class isInteger(isNumber):
	
	def validate(self, value):
		if not isinstance(value, int):
			raise ValueError('not an integer')
		super(isInteger, self).validate(value)

class isString(Validator):
	
	def __init__(self, allow_empty = True, regex = None, enum = None):
		self.allow_empty = allow_empty
		self.enum = enum
		self.regex = None
		if regex:
			if isinstance(regex, basestring):
				self.regex = regex
				pattern = regex
				flags = 0
			else: # tupple
				pattern, flags = regex
				self.regex = str(regex)
				if isinstance(flags, basestring):
					f = 0
					for c in flags:
						f = f | getattr(re, c.upper())
					flags = f
			
			self.regex_c = re.compile(pattern, flags)
	
	def validate(self, value):
		if not isinstance(value, basestring):
			raise ValueError('not a string')
		
		if not self.allow_empty and len(value)==0:
			raise ValueError('empty string')
		
		if self.regex is not None:
			if not self.regex_c.search(value):
				raise ValueError("does not match the regular expression '%s'" % self.regex)
		
		if self.enum is not None:
			if value not in self.enum:
				raise ValueError("must be one of the following values: %s." % ','.join(self.enum))
		

class isObject(Validator):
	
	def __init__(self, allow_extra = False, optionals = [], **kwargs):
		self.dict = kwargs
		self.allow_extra = allow_extra
		self.optionals = optionals
	
	def validate(self, value):
		if not isinstance(value, dict):
			raise ValueError('not an object')
		
		checked = []
		for k, v in value.iteritems():
			
			if k in self.dict:
				try:
					self.dict[k].validate(v)
				except Exception as e:
					raise type(e), type(e)(("key '%s': " % k) + e.message), sys.exc_info()[2]
			else:
				if not self.allow_extra:
					raise ValueError("unknown key '%s'" % k)
			
			checked.append(k)
		
		for k, v in self.dict.iteritems():
			if k not in checked:
				if k not in self.optionals:
					raise ValueError("the key '%s' is not present" % k)
	

class isArray(Validator):
	
	def __init__(self, item, min_len = None, max_len = None):
		self.item = item
		self.min_len = None
		self.max_len = None
	
	def validate(self, value):
		if not isinstance(value, list):
			raise ValueError('not an array')
		
		l = len(value)
		
		if self.min_len is not None:
			if l < self.min_len:
				raise ValueError('the array must contain at least %d items (got %d)' % (self.min_len, l))
		
		if self.max_len is not None:
			if l > self.max_len:
				raise ValueError('the array must contain at most %d items (got %d)' % (self.max_len, l))
		
		if l>0:
			try:
				self.item.validate(value[0])
			except Exception as e:
				raise type(e), type(e)(("the array items are invalid: " % k) + e.message), sys.exc_info()[2]
		
	
	
	

	# decorator
	
	READ_ONLY = 2
	PRIVATE = 4
	
	def attr(name, validator = isAnything(), default = None, mode = None):
		def d(cls):
			
			attributes = getattr(cls, '__attributes', {}).copy()
			
			attributes[name] = {
				'validator': validator,
				'default': default,
				'mode': mode
			}
			
			setattr(cls, '__attributes', attributes)
			
			return cls
		return d



if __name__ == "__main__":
	v = isNone() | isInteger()
	#print v, v.validate("ji")

	v = isString(regex='toto')
	v.validate('totodfs')
	
	v = isObject(optionals = ['o'], key = isString(), o = isAnything(), allow_extra = True, gt = isAnything())
	v.validate({'key': 'toto', 'tt': 78})

