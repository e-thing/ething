# coding: utf-8

from .reg import *
from future.utils import with_metaclass
from collections.abc import Mapping
import time


@namespace('signals')
@abstract
class Signal(with_metaclass(MetaReg, Mapping)):
    """
    Base class of any signal.

    To register a new signal, simply override this class ::

        class MySignal(Signal):
            pass

        my_signal = MySignal(foo="bar")

        # foo data is accessible through the data dictionary :
        my_signal.data['foo'] # = "bar"

    """

    def __init__(self, **data):
        self.type = get_definition_name(type(self))
        self.ts = time.time()
        self.data = data

    def __str__(self):
        return '<signal %s>' % self.type

    def __repr__(self):
        return str(self)

    def __getitem__(self, key):
        return self.__dict__[key]

    def __iter__(self):
        return iter(self.__dict__)

    def __len__(self):
        return len(self.__dict__)

    def __flow_msg__(self):
        return {
            '_type': self.type,
            '_ts': self.ts,
            'payload': self.data
        }

    def __json__(self):
        return self.__dict__.copy()


@abstract
class ResourceSignal(Signal):
    """
    Any signal emitted by a resource must override this class.

    To register a new signal, simply override this class ::

        class MySignal(ResourceSignal):
            pass

        my_signal = MySignal(resource, foo="bar")

        # foo data is accessible through the data dictionary :
        my_signal.data['foo'] # = "bar"

        # the resource instance is accessible through:
        my_signal.resource # Resource object

    """

    def __init__(self, resource, **data):
        super(ResourceSignal, self).__init__(**data)
        self.resource = resource

    def __str__(self):
        return "<signal %s resource=%s>" % (self.type, self.resource.id)

    def __flow_msg__(self):
        msg = super(ResourceSignal, self).__flow_msg__()
        msg['resource'] = self.resource.id
        return msg

    def __json__(self):
        # do not send the whole resource instance
        cpy = super(ResourceSignal, self).__json__()
        cpy['resource'] = self.resource.id
        return cpy


@abstract
class PluginSignal(Signal):
    """
    Any signal emitted by a plugin must override this class.
    """

    def __init__(self, plugin, **data):
        super(PluginSignal, self).__init__(**data)
        self.plugin = plugin

    def __str__(self):
        return "<signal %s plugin=%s>" % (self.type, self.plugin.name)

    def __flow_msg__(self):
        msg = super(PluginSignal, self).__flow_msg__()
        msg['plugin'] = self.plugin.name
        return msg

    def __json__(self):
        # do not send the whole resource instance
        cpy = super(PluginSignal, self).__json__()
        cpy['plugin'] = self.plugin.name
        return cpy
