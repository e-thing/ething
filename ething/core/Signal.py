# coding: utf-8

from .reg import *
from future.utils import with_metaclass
from collections import Mapping
import time


@path('signals')
@abstract
class Signal(with_metaclass(MetaReg, Mapping)):
    def __init__(self):
        self._type = type(self).__name__
        self._ts = time.time()
        self.payload = None

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
    def __init__(self, resource):
        super(ResourceSignal, self).__init__()
        self.resource = resource

    def __str__(self):
        return "<signal %s resource=%s>" % (self._type, self.resource.id)

    def toFlowMessage(self):
        msg = self.__dict__.copy()
        msg['resource'] = self.resource.id
        return msg
