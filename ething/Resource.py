# coding: utf-8

from .db import *
from .Signal import ResourceSignal
from .utils.date import TzDate, utcnow
from .utils.ObjectPath import evaluate
from .utils.logger import NamedLoggerAdapter
from .scheduler import *
from .processes import *
from .notification import NotificationManager
from .dispatcher import SignalEmitter
from collections import Mapping
import inspect
import logging


LOGGER = logging.getLogger(__name__)


@meta(icon='mdi-plus')
class ResourceCreated(ResourceSignal):
    """
    is emitted each time a resource is created
    """
    pass


@meta(icon='mdi-delete')
class ResourceDeleted(ResourceSignal):
    """
    is emitted each time a resource is deleted
    """
    pass


@meta(icon='mdi-update')
class ResourceUpdated(ResourceSignal):
    """
    is emitted each time a resource attribute has been updated
    """
    def __init__(self, resource, attributes):
        super(ResourceUpdated, self).__init__(resource, attributes=attributes)

    @property
    def attributes(self):
        return self.data['attributes']


class ResourceType(WeakDBLink):

    def __init__(self, accepted_types=None, must_throw=None, **attributes):
        super(ResourceType, self).__init__('resources/Resource', **attributes)
        self.accepted_types = None
        if accepted_types:
            self.accepted_types = list()
            for t in accepted_types:
                if inspect.isclass(t):
                    if issubclass(t, Resource):
                        t = get_definition_name(t)
                    else:
                        raise Exception('not a subclass of Resource : %s' % t)
                self.accepted_types.append(t)
        self.must_throw = must_throw
        if isinstance(self.must_throw, string_types):
            self.must_throw = get_registered_class(self.must_throw)

    def check(self, r):
        if self.accepted_types is not None:
            for t in self.accepted_types:
                if r.typeof(t):
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

    def to_shema(self, context = None):
        schema = super(ResourceType, self).to_shema(context)
        schema['$component'] = 'ething.resource'
        if self.accepted_types:
            schema['$onlyTypes'] = self.accepted_types
        if self.must_throw:
            schema['$must_throw'] = get_definition_name(self.must_throw)
        return schema


class ResourceTypeArray (WeakDBLinkArray):

    def __init__(self, accepted_types=None, must_throw=None, max_len=None, **attributes):
        attributes.setdefault('$component', 'ething.resource')
        super(ResourceTypeArray, self).__init__(ResourceType(accepted_types=accepted_types, must_throw=must_throw), max_len=max_len, **attributes)


class RDict(Dict):
    def to_json(self, value, context=None):
        """ do not show keys that starts with '_'"""
        j = {}
        for key in value:
            if not key.startswith('_'):
                item_type = self.get_type_from_key(key)
                j[key] = item_type.to_json(value[key], context)
        return j




@abstract
@throw(ResourceCreated, ResourceDeleted, ResourceUpdated)
@attr('public', type=Enum([False, 'readonly', 'readwrite']), default=False, description="False: this resource is not publicly accessible. 'readonly': this resource is accessible for reading by anyone. 'readwrite': this resource is accessible for reading and writing by anyone.")
@attr('description', type=String(), default='', description="A description of this resource.")
@attr('data', type=RDict(allow_extra=True), default={}, description="A collection of arbitrary key-value pairs.")
@attr('createdBy', type=Nullable(ResourceType()), mode=READ_ONLY, default=None, description="The id of the resource responsible of the creation of this resource, or null.")
@attr('modifiedDate', type=TzDate(), default=lambda _: utcnow(), mode=READ_ONLY, description="Last time this resource was modified")
@attr('createdDate', type=TzDate(), default=lambda _: utcnow(), mode=READ_ONLY, description="Create time for this resource")
@attr('name', type=String(allow_empty=False, regex='^[a-zA-Z0-9 !#$%&\'()+,\-.;=@^_`{    ]+(\\/[a-zA-Z0-9 !#$%&\'()+,\-.;=@^_`{    ]+)*$'), description="The name of the resource")
@discriminate('type', description="The type of the resource")
@uid(description="The id of the resource")
@db(table='resources')
@namespace('resources')
@meta(description='')
class Resource(Entity, SignalEmitter):
    """
    The Resource class is the base class of any "EThing object".

    It can be a Device, a File, a Table ...

    To register a new Resource, simply override the Resource class ::

        # use the @attr decorator to declare some specific attributes.
        @attr('foo', type=String(allow_empty=False), default='bar', description="foo attribute")
        class Foo(Resource):
            pass


    To instanciate a new Foo resource::

        core.create(Foo, {
            'name': 'john',
            'foo': 'BAR' # you can override the default here
        }) # returns a new Foo instance


    or you could also write it ::

        core.create('resources/foo", {...})

    If you want to bind asynchronous processing, you could write it ::

        @attr('count', type=Number(), default=0)
        class Foo(Resource):

            @set_interval(60) # every 60 secondes
            def async_processing(self):
                # this method is fired every minute
                self.count += 1

            @process()
            def daemon_like_async_processing(self):
                # this method is fired when the instance is created
                while True:
                    # ... do some processing here
                    time.sleep(0.1) # do not forget to give some time, sp other processes can run

    If the resource emits a signal, be sure that the signal was previously binded to the current class
    using the ``@throw`` decorator::

        class MySignal(Signal):
            pass

        @throw(Signal)
        class Foo(Resource):
            def bar(self):
                self.emit(MySignal())

    """

    def __init__(self, data=None, context=None):

        if 'core' not in context:
            raise Exception('missing "core" in context')

        super(Resource, self).__init__(data, context)

        self._logger = NamedLoggerAdapter(self, self.name)

        self._processes = ProcessCollection(parent=self)

        self._notification = NotificationManager(self.core, self)

        """
        bind processes to this instance
        1 - look for __process__ attribute which can either be :
             - a method:
               def __process__(self): return MyProcess(...)
             - a Process subclass:
               __process__ = MyProcess # will be instantiated with a single argument corresponding to the current resource
             - an array of Process subclass:
               __process__ = [MyProcess0, MyProcess1, ...]

        2 - look for any method decorated with @process

        """

        if hasattr(self, '__process__'):
            self.processes.add(self.__process__() if callable(self.__process__) else self.__process__)

        # find any @process decorator
        for p in generate_instance_processes(self):
            self.processes.add(p)

        bind_instance(self)

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
        return [get_definition_name(c) for c in type(self).__mro__ if issubclass(c, Resource)]

    def namespace(self):
        return self.core.namespace + "." + self.id

    @property
    def logger(self):
        return self._logger

    @property
    def processes(self):
        return self._processes

    @property
    def notification(self):
        """
        the notification manager
        """
        return self._notification

    def typeof(self, typename):
        """
        returns True if this instance derive from ``typename``

        :param typename: a :class:`Resource` class, a :class:`Resource` instance  or a type (eg: 'resources/Device')
        :return: boolean
        """
        if isinstance(typename, Resource):
            typename = get_definition_name(type(typename))
        elif inspect.isclass(typename) and issubclass(typename, Resource):
            typename = get_definition_name(typename)
        return typename in self.extends

    def children(self, filter=None):
        """
        List all the children of this resource. Relationship is done through the :class:`Resource.createdBy` attribute.

        :param filter: a callable to filter the returned children set
        :return: a list of :class:`Resource`
        """
        def _filter (r):
            if r.createdBy == self:
                if filter:
                    return filter(r)
                return True
            return False

        return self.core.find(_filter)

    def remove(self):
        """
        Remove this instance.
        """
        children = self.children()

        for child in children:
            child.remove()

        unbind(self)
        self.processes.stop_all()

        remove(self)

        # clear internal __dict__ entries: free memory
        # necessary to remove all refs to other objects
        for k in list(self.__dict__):
            if k is not '__reg__': # no need to remove this one
                self.__dict__.pop(k)

        # flag it as destroyed
        # avoid to be saved again by mistake
        self.__destroyed__ = True

    def __db_remove__(self):
        self.logger.info("Resource deleted")
        self.core.emit(ResourceDeleted(self))

    def __db_save__(self, insert):
        if insert:
            if getattr(self, '__destroyed__', False):
                raise Exception('this object was previously destroyed')
            self.core.emit(ResourceCreated(self))
            self.logger.info("Resource created")
            return

        self.modifiedDate = utcnow()  # update the modification time

        dirty_attrs = list_dirty_attr(self)
        dirty_keys = [a.name for a in dirty_attrs]

        self.logger.debug("Resource update, dirtyFields: %s", dirty_keys)

        history_data = {}

        for a in dirty_attrs:
            value = getattr(self, a.name)

            self.on_attr_update(a.name, value, None)

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

        self.on_update(dirty_keys)

        self.core.emit(ResourceUpdated(self, dirty_keys))

    def on_update(self, dirty_keys):
        pass

    def on_attr_update(self, attr, new_value, old_value):
        pass

    def store(self, table_name, data, name = None, table_length = 5000):
        """
        Store data in a table that is linked to this resource.

        :param table_name: the table name
        :param data: the data to store (dict, string, number, boolean)
        :param name: the name of the column (not used if the data is a dict)
        :param table_length: max length of the table. Default to 5000.
        :return: :class:`ething.Table.Table` instance.
        """
        try:
            table = self.core.find_one(
                lambda r: r.createdBy == self and r.name == table_name and r.typeof('resources/Table'))

            if not table:
                # create it !
                table = self.core.create('resources/Table', {
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

                return table
        except Exception as e:
            self.logger.exception('table store error for %s' % table_name)

    def match(self, expression):
        """
        return True if the current resource matches the given expression

        :param expression: a ObjectPath expression
        :return: boolean
        """
        return bool(evaluate(expression, self.__json__()))

