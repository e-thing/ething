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
        return type(self).__name__

    def __repr__(self):
        return type(self).__name__

    def toJson(self):
        return {
            'name': type(self).__name__,
            'ts': self.timestamp,
            'data': self.__dict__
        }

    # deprecated: just for compatibility
    def __getitem__(self, name):
        return getattr(self, name, None)
