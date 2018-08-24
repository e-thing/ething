# coding: utf-8

from .ShortId import ShortId, Id
from .dbentity import *
from .core import Core
import datetime


class ResourceType(Id):

    def __init__(self, accepted_types=None, **attributes):
        super(ResourceType, self).__init__(**attributes)
        self.accepted_types = accepted_types

    def check_existance(self, value):
        ething = Core.get_instance()
        r = ething.get(value)

        if r is None:
            raise ValueError('the resource id=%s does not exist' % value)

        if self.accepted_types is not None:
            for t in self.accepted_types:
                if r.isTypeof(t):
                    break
            else:
                raise ValueError('the Resource does not match the following types: %s' % ','.join(
                    self.accepted_types))

    def fromJson(self, value, **kwargs):
        value = super(ResourceType, self).fromJson(value)
        self.check_existance(value)
        return value


@path('resources')
@attr('public', type=Enum([False, 'readonly', 'readwrite']), default=False, description="False: this resource is not publicly accessible. 'readonly': this resource is accessible for reading by anyone. 'readwrite': this resource is accessible for reading and writing by anyone.")
@attr('description', type=String(), default='', description="A description of this resource.")
@attr('data', type=Dict(allow_extra=True), default={}, description="A collection of arbitrary key-value pairs. Entries with null values are cleared in update. The keys must not be empty or longer than 64 characters, and must contain only the following characters : letters, digits, underscore and dash. Values must be either a string or a boolean or a number")
@attr('createdBy', type=Nullable(Id()), default=None, description="The id of the resource responsible of the creation of this resource, or null.")
@attr('modifiedDate', default=lambda _: datetime.datetime.utcnow(), mode=READ_ONLY, description="Last time this resource was modified")
@attr('createdDate', default=lambda _: datetime.datetime.utcnow(), mode=READ_ONLY, description="Create time for this resource")
@attr('extends', mode=READ_ONLY, default=lambda cls: [get_definition_pathname(c) for c in cls.__mro__ if issubclass(c, Resource) and (c is not Resource)], description="An array of classes this resource is based on.")
@attr('type', mode=READ_ONLY, default=lambda cls: get_definition_pathname(cls), description="The type of the resource")
@attr('id', default=lambda _: ShortId.generate(), mode=READ_ONLY, description="The id of the resource")
@attr('name', type=String(allow_empty=False, regex='^[a-zA-Z0-9 !#$%&\'()+,\-.;=@^_`{    ]+(\\/[a-zA-Z0-9 !#$%&\'()+,\-.;=@^_`{    ]+)*$'), description="The name of the resource")
class Resource(DbEntity):
    """
    The base representation of a resource object
    """

    def __init__(self, data, create, ething):

        if isinstance(data.get('createdBy'), Resource):
            data['createdBy'] = data.get('createdBy').id

        super(Resource, self).__init__(data, create)
        object.__setattr__(self, '_Resource__ething', ething)

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
        ##id = self.id

        self.ething.resource_db_cache.remove(self)
        #c = self.ething.db["resources"]
        #c.delete_one({'_id': id})

        self.ething.log.debug("Resource deleted : %s" % str(self))

        self.ething.dispatchSignal('ResourceDeleted', self)

    def _insert(self):

        # insertion
        self.ething.resource_db_cache.insert(self)
        #c = self.ething.db["resources"]
        #try:
        #    c.insert_one(self.serialize())
        #except:
        #    # code 11000 on duplicate error
        #    raise Exception('internal error: doc insertion failed')

        self.ething.dispatchSignal('ResourceCreated', self)

        self.ething.log.debug("Resource created : %s" % str(self))

    def _before_save(self):
        self._modifiedDate = datetime.datetime.utcnow()  # update the modification time

    def _save(self, dirty_attrs):

        dirty_keys = [a.name for a in dirty_attrs]

        self.ething.log.debug("Resource update : %s , dirtyFields: %s" % (
            str(self), dirty_keys))

        self.ething.resource_db_cache.save(self)
        #c = self.ething.db["resources"]
        #c.replace_one({'_id': self.id}, self.serialize())

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
                if isinstance(value, MutableMapping):
                    history_data[name]['data'].update(value)
                else:
                    history_data[name]['data'][a.name] = value

        for table_name in history_data:

            history_data_item = history_data[table_name]

            try:
                table = self.ething.findOne(lambda r: r.createdBy == self and r.name == table_name and r.isTypeof('resources/Table'))

                if not table:
                    # create it !
                    table = self.ething.create('resources/Table', {
                        'name': table_name,
                        'createdBy': self.id,
                        'maxLength': history_data_item['length']
                    })

                if table:
                    table.insert(history_data_item['data'])
            except Exception as e:
                self.ething.log.exception('history error for %s' % table_name)

        self.ething.dispatchSignal(
            'ResourceMetaUpdated', self, list(dirty_keys))

    #def _refresh(self):
    #    #c = self.ething.db["resources"]
    #    #return c.find_one({'_id': self.id})
    #    return {}

    def match(self, expression):
        filter = self.ething.resourceQueryParser.compile(expression)
        return filter(self)

    def repair(self):
        pass
