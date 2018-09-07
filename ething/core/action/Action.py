# coding: utf-8

from ..entity import *


def _attr_signal_default(cls):
    if cls.signal is not None:
        return cls.signal.__name__
    else:
        return None


@path('actions')
@abstract
@attr('type', mode=READ_ONLY, default=lambda cls: str(cls.__name__), description="The type of the action")
class Action(Entity):

    @property
    def rule(self):
        return self.get_root()

    @property
    def ething(self):
        return self.rule.ething

    def run(self, signal):
        raise NotImplementedError()

    @classmethod
    def unserialize(cls, data, **kwargs):
        type = data.get('type')
        _cls = get_registered_class(type)
        return Entity.unserialize.__func__(_cls, data, **kwargs)

    @classmethod
    def fromJson(cls, data, **kwargs):
        type = data.get('type')
        _cls = get_registered_class(type)
        return Entity.fromJson.__func__(_cls, data, **kwargs)

