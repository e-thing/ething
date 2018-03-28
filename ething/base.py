
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

class isBool(Validator):
	
	def validate(self, value):
		if not isinstance(value, bool):
			raise ValueError('not a boolean')

class isEnum(Validator):
	def __init__(self, enum):
		self.enum = enum
	
	def validate(self, value):
		if value not in self.enum:
			raise ValueError("must be one of the following values: %s." % ','.join(str(e) for e in self.enum))

class isNumber(Validator):
	
	def __init__(self, min = None, max = None):
		self.min = min
		self.max = max
	
	def validate(self, value):
		if not isinstance(value, int) and not isinstance(value, float):
			raise ValueError('not a number')
		if self.min is not None:
			if value < self.min:
				raise ValueError('value < %s' % str(self.min))
		if self.max is not None:
			if value > self.max:
				raise ValueError('value > %s' % str(self.max))

class isInteger(isNumber):
	
	def validate(self, value):
		if not isinstance(value, int):
			raise ValueError('not an integer')
		super(isInteger, self).validate(value)

class isInstance(Validator):
	
	def __init__(self, cls):
		self.cls = cls
	
	def validate(self, value):
		if not isinstance(value, self.cls):
			raise ValueError('not an instance of "%s"' % self.cls.__name__)

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
	
	def __init__(self, allow_extra = False, extra_validator = None, optionals = [], **kwargs):
		self.dict = kwargs
		self.allow_extra = allow_extra
		self.extra_validator = None
		self.optionals = optionals
	
	def validate(self, value):
		if not isinstance(value, dict):
			raise ValueError('not an object')
		
		checked = []
		for k, v in value.iteritems():
			
			validator = None
			
			if k in self.dict:
				validator = self.dict[k]
			else:
				if not self.allow_extra:
					raise ValueError("unknown key '%s'" % k)
				else:
					if self.extra_validator:
						validator = self.extra_validator
			
			if validator:
				try:
					validator.validate(v)
				except Exception as e:
					raise type(e), type(e)(("key '%s': " % k) + e.message), sys.exc_info()[2]
			
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

class ModelAdapter(object):
	
	
	def set(self, data_object, data, name, value):
		data[name] = value
	
	def get(self, data_object, data, name):
		return data[name]
	
	def has(self, data_object, data, name):
		return name in data

default_model_adapter = ModelAdapter()

def attr(name, **kwargs):
	def d(cls):
		
		attributes = getattr(cls, '__attributes', {})
		
		attributes_cls = getattr(cls, '__attributes_cls', None)
		if attributes_cls is not None and attributes_cls != cls.__name__:
			copy_attr = {}
			for n in attributes:
				copy_attr[n] = attributes[n].copy()
			attributes = copy_attr
		
		attributes.setdefault(name, {
			'validator': None,
			'model_adapter': default_model_adapter,
			'mode': None
		})
		
		required = False
		
		for i in kwargs:
			if i == 'default':
				kwargs[i] = _make_default_fct(kwargs[i])
			if i == 'required':
				required = kwargs[i]
			else:
				attributes[name][i] = kwargs[i]
		
		# remove the default attribute !
		if required:
			if 'default' in attributes[name]:
				attributes[name].pop('default')
		
		setattr(cls, '__attributes', attributes)
		setattr(cls, '__attributes_cls', cls.__name__)
		
		return cls
	return d

def _make_default_fct(v):
	return v if callable(v) else lambda _: v




class DataObject(object):
	
	def __init__ (self, data = None):
		# make some private fields
		object.__setattr__(self, '_DataObject__new', data is None)
		object.__setattr__(self, '_DataObject__no_save', 0)
		object.__setattr__(self, '_DataObject__d', data or {})
		object.__setattr__(self, '_DataObject__dirtyFields', set())
		
		if data is None:
			attributes = getattr(self, '__attributes', {})
			for name in attributes:
				attribute = attributes[name]
				if 'default' in attribute:
					attribute['model_adapter'].set(self, self.__d, name, attribute['default'](self))
	
	def toJson(self):
		j = {}
		attributes = getattr(self, '__attributes', {})
		for name in attributes:
			attribute = attributes[name]
			if attribute.get('mode') == PRIVATE:
				continue
			model_adapter = attribute['model_adapter']
			try:
				j[name] = model_adapter.get(self, self.__d, name)
			except:
				pass
		return j
	
	def __getattr__ (self,	name ):
		
		priv_access = False
		
		if name.startswith('_'):
			priv_access = True
			name = name[1:]
		
		attribute = getattr(self, '__attributes', {}).get(name)
		
		if attribute is None:
			raise AttributeError('no attribute "%s"' % name)
		
		if attribute.get('mode') == PRIVATE and not priv_access:
			raise AttributeError('attribute "%s" is not readable' % name)
		
		model_adapter = attribute['model_adapter']
		
		if not model_adapter.has(self, self.__d, name):
			if 'default' in attribute:
				model_adapter.set(self, self.__d, name, attribute['default'](self))
			else: # mandatory but not set
				raise AttributeError('attribute "%s" is not set' % name)
		
		return model_adapter.get(self, self.__d, name)
	
	
	def __setattr__ (self,	name, value ):
		
		priv_access = False
		
		if name.startswith('_'):
			priv_access = True
			name = name[1:]
		
		attribute = getattr(self, '__attributes', {}).get(name)
		
		if attribute is None:
			raise AttributeError('no attribute "%s"' % name)
		
		mode = attribute.get('mode')
		if (mode == PRIVATE or mode == READ_ONLY) and not priv_access:
			raise AttributeError('attribute "%s" is not writable' % name)
		
		validator = attribute.get('validator')
		if validator:
			try:
				validator.validate(value)
			except ValueError as e:
				raise AttributeError('invalid attribute "%s": %s' % (name, str(e)))
		
		model_adapter = attribute['model_adapter']
		
		model_adapter.set(self, self.__d, name, value)
		
		self.setDirtyAttr(name)
		
	
	def setDirtyAttr(self, name):
		self.__dirtyFields.add(name)
	
	def hasDirtyAttr(self):
		return bool(len(self.__dirtyFields))
	
	def getDirtyAttr(self):
		return self.__dirtyFields
	
	def save(self):
		
		if len(self.__dirtyFields) == 0:
			return # nothing to save
		
		if self.__no_save > 0:
			return 
		
		# avoid infinit loop, if save() is called in _insert or _save
		object.__setattr__(self, '_DataObject__no_save', 1)
		
		try:
			
			if self.__new:
				
				attributes = getattr(self, '__attributes', {})
				for name in attributes:
					attribute = attributes[name]
					
					model_adapter = attribute.get('model_adapter', name)
					
					if not model_adapter.has(self, self.__d, name):
						raise AttributeError('attribute "%s" is not set' % name)
				
				self._insert(self.__d)
				
				object.__setattr__(self, '_DataObject__new', False)
				
			else:
				self._save(self.__d)
			
			self.__dirtyFields.clear()
		
		except:
			raise
		finally:
			object.__setattr__(self, '_DataObject__no_save', 0)
	
	
	def _insert(self, data):
		raise NotImplemented()
	
	def _save(self, data):
		raise NotImplemented()
	
	def _refresh(self):
		raise NotImplemented()
	
	def refresh (self, keepDirtyFields = False):
		doc = self._refresh()
		
		if(keepDirtyFields):
			for field in self.__dirtyFields:
				try:
					doc.pop(field)
				except KeyError:
					pass
			
			self.__d.update(doc)
		else:
			self.__dirtyFields.clear()
			self.__d.clear()
			self.__d.update(doc)
	
	def __enter__(self):
		object.__setattr__(self, '_DataObject__no_save', self.__no_save + 1) # necessary to take into account nested with statements
		return self
	
	def __exit__(self, type, value, traceback):
		object.__setattr__(self, '_DataObject__no_save', self.__no_save - 1) # necessary to take into account nested with statements
		self.save()
	

if __name__ == "__main__":
	import datetime

	class isResource(Validator):
		
		def validate(self, value):
			if not isinstance(value, Resource):
				raise ValueError('not a Resource')

	class isId(Validator):
		def validate(self, value):
			if not isinstance(value, basestring) or not re.search('^[-_a-zA-Z0-9]{7}$', value):
				raise ValueError('not an id')


	class IdModelAdapter(ModelAdapter):
		
		def set(self, data_object, data, name, value):
			data['_id'] = value
		
		def get(self, data_object, data, name):
			return data['_id']
		
		def has(self, data_object, data, name):
			return '_id' in data

	class CreatedByModelAdapter(ModelAdapter):
		
		def set(self, data_object, data, name, value):
			data[name] = value.id if isinstance(value, Resource) else value
		
	class DataModelAdapter(ModelAdapter):
		
		def set(self, data_object, data, name, value):
			if name in data:
				data[name].update(value)
			else:
				data[name] = {}
			
			# remove keys with None value
			for k in data[name].keys():
				if data[name][k] is None:
					data[name].pop(k)

	@attr('name', validator = isString(allow_empty = False))
	@attr('id', default = 'myid', mode = READ_ONLY, model_adapter = IdModelAdapter())
	@attr('createdDate', default = lambda _: datetime.datetime.utcnow(), mode = READ_ONLY)
	@attr('createdBy', validator = isResource() | isNone() | isId(), default = None, model_adapter = CreatedByModelAdapter())
	@attr('private', mode = PRIVATE, default = None)
	@attr('data', validator = isObject(allow_extra = True, extra_validator = isString() | isNumber | isNone() | isBool()), default = {}, model_adapter = DataModelAdapter())
	class Resource(DataObject):
		
		def _insert(self, data):
			print "insert =>", data
		
		def _save(self, data):
			print "save =>", data
			
		
		def __getattr__ (self,	name ):
			
			value = super(Resource, self).__getattr__(name)
			
			if name == 'createdBy':
				#return data_object.ething.get(value)
				return 'yyo'
			else:
				return value
	
	
	@attr('id', default = 'gtY')
	class S(Resource):
		pass
	
	print getattr(Resource, '__attributes', {})
	print getattr(S, '__attributes', {})
	r = S()
	r.name = "tata"
	r.createdBy = r
	r._private = 'toto'
	print r.id
	print r.createdBy
	r.data = {
		'aa': 'AA',
		'fd': None
	}
	r.data = {
		'bb': 'BBB'
	}
	r.save()

	print r.toJson()


