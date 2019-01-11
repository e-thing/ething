# coding: utf-8

from .reg import *
from future.utils import with_metaclass
import time


@path('signals')
@abstract
class Signal(with_metaclass(MetaReg, object)):

    def __init__(self):
        super(Signal, self).__setattr__('_Signal__ts', time.time())

    @property
    def timestamp(self):
        return self.__ts

    def __str__(self):
        return '<signal %s>' % type(self).__name__

    def __repr__(self):
        return str(self)

    def toJson(self):
        data = {}
        for k in self.__dict__:
            if not k.startswith('_'):
                data[k] = self.__dict__[k]
        return {
            'name': type(self).__name__,
            'ts': self.timestamp,
            'data': data
        }

    # deprecated: just for compatibility
    def __getitem__(self, name):
        return getattr(self, name, None)


@abstract
class ResourceSignal(Signal):
    def __init__(self, resource):
        super(ResourceSignal, self).__init__()
        self.resource = resource

    def __str__(self):
        return "<signal %s resource=%s>" % (type(self).__name__, self.resource.id)

