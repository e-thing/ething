# coding: utf-8

from .db import *
from .Signal import ResourceSignal
from .Interface import Interface
from .utils.date import TzDate, utcnow
from .utils.objectpath import evaluate
from .utils.ShortId import Id
from collections import Mapping
import inspect
import logging


@namespace('resources', True)
@meta(icon='mdi-plus')
class ResourceCreated(ResourceSignal):
    """
    is emitted each time a resource is created
    """
    pass


@namespace('resources', True)
@meta(icon='mdi-delete')
class ResourceDeleted(ResourceSignal):
    """
    is emitted each time a resource is deleted
    """
    pass


@namespace('resources', True)
@meta(icon='mdi-update')
class ResourceUpdated(ResourceSignal):
    """
    is emitted each time a resource attribute has been updated
    """
    def __init__(self, resource, attributes):
        super(ResourceUpdated, self).__init__(resource)
        self.payload = {
            'attributes': attributes
        }

    @property
    def attributes(self):
        return self.payload['attributes']


class ResourceType(Id):

    def __init__(self, accepted_types=None, must_throw=None, **attributes):
        super(ResourceType, self).__init__(**attributes)
        self.accepted_types = accepted_types
        self.must_throw = must_throw
        if isinstance(self.must_throw, string_types):
            self.must_throw = get_registered_class(self.must_throw)


    def check_existance(self, value, context = {}):
        ething = context.get('ething')
        if ething:
            r = ething.get(value)

            if r is None:
                raise ValueError('the resource id=%s does not exist' % value)

            if self.accepted_types is not None:
                for t in self.accepted_types:
                    if r.isTypeof(t):
                        break
                else:
                    raise ValueError('the Resource %s does not match the following types: %s' % (r, ','.join(
                        self.accepted_types)))

            if self.must_throw:
                signals_thrown_by_resource = [s.signal for s in list_registered_signals(r)]
                signal = self.must_throw
                if signal not in signals_thrown_by_resource:
                    raise ValueError("the resource %s does not throw the signal : %s" % (
                        r, get_definition_name(signal)))

    def fromJson(self, value, context=None):
        value = super(ResourceType, self).fromJson(value, context)
        self.check_existance(value, context)
        return value

    def toSchema(self, context = None):
        schema = super(ResourceType, self).toSchema(context)
        schema['$component'] = 'ething.resource'
        if self.accepted_types:
            schema['$onlyTypes'] = self.accepted_types
        if self.must_throw:
            schema['$must_throw'] = get_definition_name(self.must_throw)
        return schema


class RDict(Dict):
    def toJson(self, value, context=None):
        """ do not show keys that starts with '_'"""
        j = {}
        for key in value:
            if not key.startswith('_'):
                item_type = self.get_type_from_key(key)
                j[key] = item_type.toJson(value[key], context)
        return j


@throw(ResourceCreated, ResourceDeleted, ResourceUpdated)
@attr('public', type=Enum([False, 'readonly', 'readwrite']), default=False, description="False: this resource is not publicly accessible. 'readonly': this resource is accessible for reading by anyone. 'readwrite': this resource is accessible for reading and writing by anyone.")
@attr('description', type=String(), default='', description="A description of this resource.")
@attr('data', type=RDict(allow_extra=True), default={}, description="A collection of arbitrary key-value pairs.")
@attr('createdBy', type=Nullable(DBLink('resources/Resource')), default=None, description="The id of the resource responsible of the creation of this resource, or null.")
@attr('modifiedDate', type=TzDate(), default=lambda _: utcnow(), mode=READ_ONLY, description="Last time this resource was modified")
@attr('createdDate', type=TzDate(), default=lambda _: utcnow(), mode=READ_ONLY, description="Create time for this resource")
@attr('name', type=String(allow_empty=False, regex='^[a-zA-Z0-9 !#$%&\'()+,\-.;=@^_`{    ]+(\\/[a-zA-Z0-9 !#$%&\'()+,\-.;=@^_`{    ]+)*$'), description="The name of the resource")
@discriminate(description="The type of the resource")
@uid(description="The id of the resource")
@db(table='resources')
@namespace('resources')
class Resource(Entity):

    def __init__(self, data, context=None):

        if 'ething' not in context:
            raise Exception('missing "ething" in context')

        super(Resource, self).__init__(data, context)

        self._log = logging.getLogger('ething.r.%s' % data.get('id'))
        self._t = transaction(self)

        self.ething.scheduler.bind_instance(self)

    def __eq__(self, other):
        if isinstance(other, Resource):
            return self.id == other.id
        elif isinstance(other, string_types):
            return self.id == other
        else:
            return False

    def __str__(self):
        return '<%s id=%s name=%s>' % (self.type, self.id, self.name)

    def __repr__(self):
        return str(self)

    def __hash__(self):
        return hash(self.id)

    # avoid copying
    def __copy__(self):
        return self

    # avoid copying
    def __deepcopy__(self, memo):
        return self

    @attr(description="An array of classes this resource is based on.")
    def extends(self):
        return [get_definition_name(c) for c in type(self).__mro__ if issubclass(c, Entity) and (c is not Entity and c is not Resource and c is not Interface)]

    @property
    def log(self):
        return self._log

    def isTypeof(self, typename):
        if isinstance(typename, Resource):
            typename = get_definition_name(type(typename))
        elif inspect.isclass(typename) and issubclass(typename, Resource):
            typename = get_definition_name(typename)
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

    def _removeParent(self):
        with self:
            self.createdBy = None

    def remove(self, removeChildren=False):

        children = self.children()

        remove(self)

        self.ething.scheduler.unbind(self)

        for child in children:
            if removeChildren:
                child.remove(removeChildren)
            else:
                # remove the relationship
                child._removeParent()

    def __db_remove__(self):
        self.log.debug("Resource deleted : %s" % str(self))
        self.ething.dispatchSignal(ResourceDeleted(self))

    def __db_save__(self, insert):
        if insert:
            self.ething.dispatchSignal(ResourceCreated(self))
            self.log.debug("Resource created : %s" % str(self))
            return

        self.modifiedDate = utcnow()  # update the modification time

        dirty_attrs = list_dirty_attr(self)
        dirty_keys = [a.name for a in dirty_attrs]

        self.log.debug("Resource update : %s , dirtyFields: %s" % (
            str(self), dirty_keys))

        history_data = {}

        for a in dirty_attrs:
            value = getattr(self, a.name)

            if a.get('watch'):
                self._watch(a.name, value, None)

            if a.get('history'):
                name = a.get('history_name', a.name)
                if name not in history_data:
                    history_data[name] = {
                        'length': a.get('history_length', 5000),
                        'data': {}
                    }

                if isinstance(value, Mapping):
                    history_data[name]['data'].update(value)
                else:
                    history_data[name]['data'][a.name] = value

        for table_name in history_data:
            history_data_item = history_data[table_name]
            self.store(table_name, history_data_item['data'], table_length = history_data_item['length'])

        self.ething.dispatchSignal(ResourceUpdated(self, list(dirty_keys)))

    def _watch(self, attr, new_value, old_value):
        pass

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
        return bool(evaluate(expression, self.toJson()))

    def __enter__(self):
        self._t.__enter__()
        return self

    def __exit__(self, type, value, traceback):
        self._t.__exit__(type, value, traceback)

    def export_instance(self):
        return serialize(self)

    @classmethod
    def import_instance(cls, data, context=None):
        instance = unserialize(cls, data, context)
        core.db.os.save(instance)
        return instance


