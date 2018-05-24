# coding: utf-8

from future.utils import with_metaclass, string_types
import string
import re
import sys
import copy
import datetime
from .ShortId import ShortId
from .Helpers import dict_recursive_update
from .meta import MetaResource
from .base import attr, DataObject, isBool, isString, isNone, isNumber, isObject, isEnum, READ_ONLY, PRIVATE, ModelAdapter, Validator
from future.utils import iteritems


class isResource(isString):

    def __init__(self, accepted_types=None):
        super(isResource, self).__init__(regex='^[-_a-zA-Z0-9]{7}$')
        self.accepted_types = accepted_types

    def validate(self, value, object):
        if isinstance(value, string_types):
            try:
                value = super(isResource, self).validate(value, object)
            except ValueError:
                raise ValueError('not an id')

            r = object.ething.get(value)

            if r is None:
                raise ValueError('the resource id=%s does not exist' % value)

            value = r

        elif not isinstance(value, Resource):
            raise ValueError('not a Resource')

        if self.accepted_types is not None:
            for t in self.accepted_types:
                if value.isTypeof(t):
                    break
            else:
                raise ValueError('the Resource does not match the following types: %s' % ','.join(
                    self.accepted_types))

        return value


class ResourceModelAdapter(ModelAdapter):

    def set(self, data_object, data, name, value):
        data[name] = value.id if isinstance(value, Resource) else value


class DataModelAdapter(ModelAdapter):

    def set(self, data_object, data, name, value):
        for k in list(value):
            if value[k] is None:
                value.pop(k)
        data[name] = value


@attr('name', validator=isString(allow_empty=False, regex='^[a-zA-Z0-9 !#$%&\'()+,\-.;=@^_`{    ]+(\\/[a-zA-Z0-9 !#$%&\'()+,\-.;=@^_`{    ]+)*$'), description="The name of the resource")
@attr('id', default=lambda _: ShortId.generate(), mode=READ_ONLY, model_key='_id', description="The id of the resource")
@attr('type', mode=READ_ONLY, default=lambda cls: str(cls.__name__), description="The type of the resource")
@attr('extends', mode=READ_ONLY, default=lambda cls: [c.__name__ for c in cls.__mro__ if issubclass(c, Resource) and (c is not Resource)], description="An array of classes this resource is based on.")
@attr('createdDate', default=lambda _: datetime.datetime.utcnow(), mode=READ_ONLY, description="Create time for this resource")
@attr('modifiedDate', default=lambda _: datetime.datetime.utcnow(), mode=READ_ONLY, description="Last time this resource was modified")
@attr('createdBy', validator=isResource() | isNone(), default=None, model_adapter=ResourceModelAdapter(), description="The id of the resource responsible of the creation of this resource, or null.")
@attr('data', validator=isObject(allow_extra=isString() | isNumber() | isNone() | isBool()), default={}, model_adapter=DataModelAdapter(), description="A collection of arbitrary key-value pairs. Entries with null values are cleared in update. The keys must not be empty or longer than 64 characters, and must contain only the following characters : letters, digits, underscore and dash. Values must be either a string or a boolean or a number")
@attr('description', validator=isString(), default='', description="A description of this resource.")
@attr('public', validator=isEnum([False, 'readonly', 'readwrite']), default=False, description="False: this resource is not publicly accessible. 'readonly': this resource is accessible for reading by anyone. 'readwrite': this resource is accessible for reading and writing by anyone.")
class Resource(with_metaclass(MetaResource, DataObject)):
    """
    The base representation of a resource object
    """

    def __init__(self, ething, data=None):
        object.__setattr__(self, '_Resource__ething', ething)
        super(Resource, self).__init__(data=data)

    def __str__(self):
        return '%s(id=%s, name=%s)' % (self.type, self.id, self.name)

    def __repr__(self):
        return '%s(id=%s, name=%s)' % (self.type, self.id, self.name)

    @property
    def ething(self):
        return self.__ething

    def __getattr__(self,    name):
        value = super(Resource, self).__getattr__(name)

        if name == 'createdBy' and value is not None:
            return self.ething.get(value)
        else:
            return value

    def isTypeof(self, type):
        return type in self.extends

    def dispatchSignal(self, signal, *args, **kwargs):
        self.ething.dispatchSignal(signal, *args, **kwargs)

    """ internal data getter/setter    """

    def getData(self, name, default=None):
        return self.data.get(name, default)

    def setData(self, name, value=None):
        if isinstance(name, dict):
            self.data.update(name)
        else:
            self.data[name] = value
        self.setDirtyAttr('data')
        self.save()

    def hasData(self, name):
        return name in self.data

    def removeData(self, name):
        try:
            self.data.pop(name)
        except KeyError:
            return
        else:
            self.setDirtyAttr('data')
            self.save()

    def children(self, filter=None):
        q = {
            'createdBy': self.id
        }

        if filter is not None:
            q = {
                '$and': [q, filter]
            }

        return self.ething.find(q)

    def removeParent(self):
        self.createdBy = None
        self.save()

    def remove(self, removeChildren=False):

        id = self.id
        children = self.children()

        c = self.ething.db["resources"]
        c.delete_one({'_id': id})

        self.ething.log.debug("Resource deleted : %s" % str(self))

        self.ething.dispatchSignal('ResourceDeleted', self)

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

        self.ething.dispatchSignal('ResourceCreated', self)

        self.ething.log.debug("Resource created : %s" % str(self))

    def _save(self, data):

        self.ething.log.debug("Resource update : %s , dirtyFields: %s" % (
            str(self), self.getDirtyAttr()))
        self._modifiedDate = datetime.datetime.utcnow()  # update the modification time

        c = self.ething.db["resources"]
        c.replace_one({'_id': self.id}, data)

        self.ething.dispatchSignal(
            'ResourceMetaUpdated', self, list(self.getDirtyAttr()))

    def _refresh(self):
        c = self.ething.db["resources"]
        return c.find_one({'_id': self.id})

    def match(self, expression):
        return self.ething.find_one({
            '$and': [
                {'_id': self.id},
                # use the parser because of the 'me' constant !
                self.ething.resourceQueryParser.parse(expression)
            ]
        }) is not None

    def repair(self):
        pass
