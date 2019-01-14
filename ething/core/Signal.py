# coding: utf-8

from .reg import *
from future.utils import with_metaclass
from collections import Mapping
import time


@path('signals')
@abstract
class Signal(with_metaclass(MetaReg, Mapping)):
    def __init__(self):
        object.__setattr__(self, '_Signal__ts', time.time())
        object.__setattr__(self, '_Signal__data', None)

    @property
    def _timestamp(self):
        return self.__ts

    @property
    def _data(self):
        if self.__data is None:
            self.__data = {}
            for k in self.__dict__:
                if not k.startswith('_'):
                    self.__data[k] = self.__dict__[k]
        return self.__data

    def __str__(self):
        return '<signal %s>' % type(self).__name__

    def __repr__(self):
        return str(self)

    def toJson(self):
        return {
            'name': type(self).__name__,
            'ts': self._timestamp,
            'data': self._data
        }

    def __getitem__(self, key):
        return self._data[key]

    def __iter__(self):
        return iter(self._data)

    def __len__(self):
        return len(self._data)


@abstract
class ResourceSignal(Signal):
    def __init__(self, resource):
        super(ResourceSignal, self).__init__()
        self.resource = resource

    def __str__(self):
        return "<signal %s resource=%s>" % (type(self).__name__, self.resource.id)

