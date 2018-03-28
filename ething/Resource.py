
	

"""
	 @swagger-definition
	 "Resource":{ 
	   "type": "object",
	   "description": "The base representation of a resource object",
	   "required":["name"],
	   "discriminator": "type",
	 	 "properties":{
	 		"id":{  
	 		   "type":"string",
	 		   "description":"The id of the resource.",
	         "readOnly": true
	 		},
	 		"name":{  
	 		   "type":"string",
	 		   "description":"The name of the resource."
	 		},
	 		"type":{  
	 		   "type":"string",
	 		   "description":"The type of the resource.",
	         "readOnly": true
	 		},
	 		"createdDate":{  
	 		   "type":"string",
	 		   "format":"date-time",
	 		   "description":"Create time for this resource (formatted RFC 3339 timestamp).",
	         "readOnly": true
	 		},
	 		"modifiedDate":{  
	 		   "type":"string",
	 		   "format":"date-time",
	 		   "description":"Last time this resource was modified (formatted RFC 3339 timestamp).",
	         "readOnly": true
	 		},
	 		"createdBy":{  
			   "type":"string",
			   "description":"id."
	         },
	 		   "description":"The id of the resource responsible of the creation of this resource, or null.",
	         "readOnly": true
	 		},
	 		"description":{  
	 		   "type":"string",
	 		   "description":"A description of this resource. Limited to 4096 characters"
	 		},
	 		"data":{  
	 		   "type":"object",
	 		   "description":"A collection of arbitrary key-value pairs. Entries with null values are cleared in update. The keys must not be empty or longer than 64 characters, and must contain only the following characters : letters, digits, underscore and dash. Values must be either a string or a boolean or a number"
	 		},
	 		"public":{  
	 		   "type":"boolean",
	 		   "description":"False: this resource is not publicly accessible. 'readonly': this resource is accessible for reading by anyone. 'readwrite': this resource is accessible for reading and writing by anyone."
	 		}
	 	 }
	 }
"""

import string
import re
import sys
import copy
import datetime
from ShortId import ShortId
from Helpers import dict_recursive_update
from rule.event import ResourceCreated, ResourceDeleted, ResourceMetaUpdated
from meta import MetaResource
from base import attr, DataObject, isBool, isString, isNone, isNumber, isObject, READ_ONLY, PRIVATE, ModelAdapter, Validator


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
		for k in value.keys():
			if value[k] is None:
				value.pop(k)
		data[name] = value
	

@attr('name', validator = isString(allow_empty = False, regex = '^[a-zA-Z0-9 !#$%&\'()+,\-.;=@^_`{	]+(\\/[a-zA-Z0-9 !#$%&\'()+,\-.;=@^_`{	]+)*$'))
@attr('id', default = lambda _: ShortId.generate(), mode = READ_ONLY, model_adapter = IdModelAdapter())
@attr('type', mode = READ_ONLY, default = lambda self: str(self.__class__.__name__))
@attr('extends', mode = READ_ONLY, default = lambda self: [c.__name__ for c in self.__class__.__mro__ if issubclass(c,Resource) and (c is not Resource)])
@attr('createdDate', default = lambda _: datetime.datetime.utcnow(), mode = READ_ONLY)
@attr('modifiedDate', default = lambda _: datetime.datetime.utcnow())
@attr('createdBy', validator = isResource() | isNone() | isId(), default = None, model_adapter = CreatedByModelAdapter())
@attr('data', validator = isObject(allow_extra = True, extra_validator = isString() | isNumber | isNone() | isBool()), default = {}, model_adapter = DataModelAdapter())
@attr('description', validator = isString() | isNone(), default = None)
@attr('public', validator = isBool() | isString(enum=['readonly', 'readwrite']), default = False)
class Resource(DataObject):
	
	__metaclass__ = MetaResource
	
	
	def __init__ (self, ething, data = None):
		object.__setattr__(self, '_Resource__ething', ething)
		super(Resource, self).__init__(data = data)
	
	
	def __str__(self):
		return '%s(id=%s, name=%s)' % (self.type, self.id, self.name)
	
	def __repr__(self):
		return '%s(id=%s, name=%s)' % (self.type, self.id, self.name)
	
	@property
	def ething (self):
		return self.__ething
	
	def __getattr__ (self,	name ):
		value = super(Resource, self).__getattr__(name)
		
		if name == 'createdBy' and value is not None:
			return self.ething.get(value)
		else:
			return value
	
	def isTypeof (self, type):
		return type in self.extends
	
	
	def dispatchSignal (self, signal, *args, **kwargs):
		self.ething.dispatchSignal(signal, *args, **kwargs)
	
	
	
	""" internal data getter/setter	"""
	
	def getData (self, name, default = None):
		return self.data.get(name, default)
	
	
	def setData (self, name, value = None):
		if isinstance(name, dict):
			self.data.update(name)
		else:
			self.data[name] = value
		self.setDirtyAttr('data')
		self.save()
	
	
	def hasData (self, name):
		return name in self.data
	
	
	def removeData (self, name):
		try:
			self.data.pop(name)
		except KeyError:
			return
		else:
			self.setDirtyAttr('data')
			self.save()
	
	
	
	
	def removeParent (self):
		child.createdBy = None
		child.save()
	
	
	
	def remove (self, removeChildren = False):
		
		id = self.id
		
		c = self.ething.db["resources"]
		c.delete_one({'_id' : id})
		
		self.ething.log.debug("Resource deleted : %s" % str(self))
		
		self.ething.dispatchSignal(ResourceDeleted.emit(self))
		
		children = self.ething.find({
			'createdBy' : id
		})
		
		for child in children:
			if removeChildren:
				child.remove(removeChildren)
			else:
				# remove the relationship
				child.removeParent()
	
	def _insert(self, data):
		
		# insertion
		c = self.ething.db["resources"]
		try:
			c.insert_one(data)
		except:
			# code 11000 on duplicate error
			raise Exception('internal error: doc insertion failed')
		
		self.ething.dispatchSignal(ResourceCreated.emit(self))
		
		self.ething.log.debug("Resource created : %s" % str(self))
		
	
	def _save(self, data):
		
		self.ething.log.debug("Resource update : %s , dirtyFields: %s" % (str(self), self.getDirtyAttr()))
		self.modifiedDate = datetime.datetime.utcnow() # update the modification time
		
		c = self.ething.db["resources"]
		c.replace_one({'_id' : self.id}, data)
		
		self.ething.dispatchSignal(ResourceMetaUpdated.emit(self, list(self.getDirtyAttr())))
	
	def _refresh(self):
		c = self.ething.db["resources"]
		return c.find_one({'_id' : self.id})
	
	
	# create a new resource
	@classmethod
	def create(cls, ething, attr):
		
		r = cls(ething)
		
		for k, v in attr.iteritems():
			setattr(r, k, v)
		
		r.save()
		
		return r
	
	
	def match (self, expression):
		return self.ething.find_one( {
			'$and' : [
				{ '_id' : self.id },
				self.ething.resourceQueryParser.parse(expression) # use the parser because of the 'me' constant !
			]
		} ) is not None
	
	
	def repair (self):
		pass
	
	

