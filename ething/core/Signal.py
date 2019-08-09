# coding: utf-8

from .reg import *
from future.utils import with_metaclass
from collections import Mapping
import time


@namespace('signals')
@abstract
class Signal(with_metaclass(MetaReg, Mapping)):
    """
    Base class of any signal.

    To register a new signal, simply override this class ::

        class MySignal(Signal):
            def __init__(self, some_attribute):
                super(MySignal, self).__init__()
                self.some_attribute = some_attribute

    """
    def __init__(self):
        self._type = get_definition_name(type(self))
        self._ts = time.time()
        self.payload = dict()

    def __str__(self):
        return '<signal %s>' % self._type

    def __repr__(self):
        return str(self)

    def __getitem__(self, key):
        return self.__dict__[key]

    def __iter__(self):
        return iter(self._data)

    def __len__(self):
        return len(self._data)

    def toFlowMessage(self):
        return self.__dict__


@abstract
class ResourceSignal(Signal):
    """
    Any signal emitted by a resource must override this class.

    To register a new signal, simply override this class ::

        class MySignal(ResourceSignal):
            def __init__(self, resource, some_attribute):
                super(MySignal, self).__init__(resource)
                self.some_attribute = some_attribute

    """
    def __init__(self, resource):
        super(ResourceSignal, self).__init__()
        self.resource = resource

    def __str__(self):
        return "<signal %s resource=%s>" % (self._type, self.resource.id)

    def toFlowMessage(self):
        msg = self.__dict__.copy()
        msg['resource'] = self.resource.id
        return msg
