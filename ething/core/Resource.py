# coding: utf-8

from .ShortId import ShortId, Id
from .dbentity import *
from .reg import get_definition_pathname
from .rule.event import ResourceEvent, ResourceSignal
from .Interface import Interface
from collections import Mapping
import datetime
import inspect
import logging


class ResourceCreated(ResourceSignal):
    pass


class ResourceCreatedEvent(ResourceEvent):
    """
    is emitted each time a resource is created
    """
    signal = ResourceCreated


class ResourceDeleted(ResourceSignal):
    pass


class ResourceDeletedEvent(ResourceEvent):
    """
    is emitted each time a resource is deleted
    """
    signal = ResourceDeleted


class ResourceUpdated(ResourceSignal):

    def __init__(self, resource, attributes):
        super(ResourceUpdated, self).__init__(resource)
        self.attributes = attributes


@attr('attributes', type=Nullable(Array(min_len=1, item=String(allow_empty=False))), default=None)
class ResourceUpdatedEvent(ResourceEvent):
    """
    is emitted each time a resource attribute has been updated
    """

    signal = ResourceUpdated

    def _filter(self, signal, core, rule):

        if super(ResourceUpdatedEvent, self)._filter(signal, core, rule):
            a = self.attributes

            if not a:
                return True

            b = signal.attributes
            for val in a:
                if val in b:
                    return True

        return False


class ResourceType(Id):

    def __init__(self, accepted_types=None, **attributes):
        super(ResourceType, self).__init__(**attributes)
        self.accepted_types = accepted_types

    def check_existance(self, value, context = {}):
        ething = context.get('ething')
        if ething and ething.is_db_loaded:
            r = ething.get(value)  # raise an exception if the db is not already started

            if r is None:
                raise ValueError('the resource id=%s does not exist' % value)

            if self.accepted_types is not None:
                for t in self.accepted_types:
                    if r.isTypeof(t):
                        break
                else:
                    raise ValueError('the Resource does not match the following types: %s' % ','.join(
                        self.accepted_types))

    def fromJson(self, value, context=None):
        value = super(ResourceType, self).fromJson(value, context)
        self.check_existance(value, context)
        return value


class RDict(Dict):
    def toJson(self, value, context=None):
        """ do not show keys that starts with '_'"""
        j = {}
        for key in value:
            if not key.startswith('_'):
                item_type = self.get_type_from_key(key)
                j[key] = item_type.toJson(value[key], context)
        return j


def compute_extends(cls):
    return [get_definition_pathname(c) for c in cls.__mro__ if issubclass(c, DbEntity) and (c is not DbEntity and c is not Resource and c is not Interface)]


@throw(ResourceCreated, ResourceDeleted, ResourceUpdated)
@path('resources')
@attr('public', type=Enum([False, 'readonly', 'readwrite']), default=False, description="False: this resource is not publicly accessible. 'readonly': this resource is accessible for reading by anyone. 'readwrite': this resource is accessible for reading and writing by anyone.")
@attr('description', type=String(), default='', description="A description of this resource.")
@attr('data', type=RDict(allow_extra=True), default={}, description="A collection of arbitrary key-value pairs.")
@attr('createdBy', type=Nullable(Id()), default=None, description="The id of the resource responsible of the creation of this resource, or null.")
@attr('modifiedDate', default=lambda _: datetime.datetime.utcnow(), mode=READ_ONLY, description="Last time this resource was modified")
@attr('createdDate', default=lambda _: datetime.datetime.utcnow(), mode=READ_ONLY, description="Create time for this resource")
@attr('extends', mode=READ_ONLY, default=compute_extends, description="An array of classes this resource is based on.")
@attr('type', mode=READ_ONLY, default=lambda cls: get_definition_pathname(cls), description="The type of the resource")
@attr('id', default=lambda _: ShortId.generate(), mode=READ_ONLY, description="The id of the resource")
@attr('name', type=String(allow_empty=False, regex='^[a-zA-Z0-9 !#$%&\'()+,\-.;=@^_`{    ]+(\\/[a-zA-Z0-9 !#$%&\'()+,\-.;=@^_`{    ]+)*$'), description="The name of the resource")
class Resource(DbEntity):
    """
    The base representation of a resource object
    """

    def __init__(self, data, create=True, context=None):

        if 'ething' not in context:
            raise Exception('missing "ething" in context')

        if isinstance(data.get('createdBy'), Resource):
            data['createdBy'] = data.get('createdBy').id

        super(Resource, self).__init__(data, create, context)

        object.__setattr__(self, '_Resource__ething', context.get('ething'))
        object.__setattr__(self, '_Resource__log', logging.getLogger('ething.r.%s' % data.get('id')))

        self.ething.scheduler.bind_instance(self)

    def __eq__(self, other):
        if isinstance(other, Resource):
            return self.id == other.id
        else:
            return False

    def __str__(self):
        return '%s(id=%s, name=%s)' % (self.type, self.id, self.name)

    def __repr__(self):
        return '%s(id=%s, name=%s)' % (self.type, self.id, self.name)

    def __hash__(self):
        return hash(self.id)

    @property
    def ething(self):
        return self.__ething

    @property
    def log(self):
        return self.__log

    def __getattr__(self,    name):
        value = super(Resource, self).__getattr__(name)

        if name == 'createdBy' and value is not None:
            return self.ething.get(value)
        else:
            return value

    def isTypeof(self, typename):
        if isinstance(typename, Resource):
            typename = get_definition_pathname(type(typename))
        elif inspect.isclass(typename) and issubclass(typename, Resource):
            typename = get_definition_pathname(typename)
        return typename in self.extends

    def dispatchSignal(self, signal, *args, **kwargs):
        self.ething.dispatchSignal(signal, *args, **kwargs)

    def children(self, filter=None):

        def _filter (r):
            if r.createdBy == self:
                if filter:
                    return filter(r)
                return True
            return False

        return self.ething.find(_filter)

    def removeParent(self):
        with self:
            self.createdBy = None

    def remove(self, removeChildren=False):

        children = self.children()

        super(Resource, self).remove()

        for child in children:
            if removeChildren:
                child.remove(removeChildren)
            else:
                # remove the relationship
                child.removeParent()

    def _remove(self, removeChildren=False):

        self.ething.resource_db_cache.remove(self)

        self.log.debug("Resource deleted : %s" % str(self))

        self.ething.dispatchSignal(ResourceDeleted(self))

    def _insert(self):

        # insertion
        self.ething.resource_db_cache.insert(self)

        self.ething.dispatchSignal(ResourceCreated(self))

        self.log.debug("Resource created : %s" % str(self))

    def _before_save(self):
        self.modifiedDate = datetime.datetime.utcnow()  # update the modification time

    def _save(self, dirty_attrs):

        dirty_keys = [a.name for a in dirty_attrs]

        self.log.debug("Resource update : %s , dirtyFields: %s" % (
            str(self), dirty_keys))

        self.ething.resource_db_cache.save(self)

        history_data = {}

        for a in dirty_attrs:
            if a.get('history'):
                name = a.get('history_name', a.name)
                if name not in history_data:
                    history_data[name] = {
                        'length': a.get('history_length', 5000),
                        'data': {}
                    }

                value = self._get(a)
                if isinstance(value, Mapping):
                    history_data[name]['data'].update(value)
                else:
                    history_data[name]['data'][a.name] = value

        for table_name in history_data:
            history_data_item = history_data[table_name]
            self.store(table_name, history_data_item['data'], table_length = history_data_item['length'])

        self.ething.dispatchSignal(ResourceUpdated(self, list(dirty_keys)))

    def store(self, table_name, data, name = None, table_length = 5000):
        try:
            table = self.ething.findOne(
                lambda r: r.createdBy == self and r.name == table_name and r.isTypeof('resources/Table'))

            if not table:
                # create it !
                table = self.ething.create('resources/Table', {
                    'name': table_name,
                    'createdBy': self.id,
                    'maxLength': table_length
                })

            if table:

                if not isinstance(data, Mapping):
                    if not name:
                        name = table_name
                    data = {
                        name: data
                    }

                table.insert(data)
        except Exception as e:
            self.log.exception('history error for %s' % table_name)

    def match(self, expression):
        filter = self.ething.resourceQueryParser.compile(expression)
        return filter(self)

    def repair(self, readonly = False):
        with self:
            extends = compute_extends(type(self))
            if extends != self.extends:
                self.log.warning('extends attribute must be updated')
                if not readonly:
                    self.extends = extends
