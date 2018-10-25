# coding: utf-8

from ...entity import *
import logging


@path('actions')
@abstract
@attr('type', mode=READ_ONLY, default=lambda cls: str(cls.__name__), description="The type of the action")
class Action(Entity):

    @property
    def log(self):
        return logging.getLogger('ething.%s' % self.type)

    def run(self, signal, core, rule):
        raise NotImplementedError()

    @classmethod
    def unserialize(cls, data, **kwargs):
        type = data.get('type')
        _cls = get_registered_class(type)
        if _cls is None:
            raise Exception('unknown type "%s"' % type)
        return Entity.unserialize.__func__(_cls, data, **kwargs)

    @classmethod
    def fromJson(cls, data, **kwargs):
        type = data.get('type')
        _cls = get_registered_class(type)
        if _cls is None:
            raise Exception('unknown type "%s"' % type)
        return Entity.fromJson.__func__(_cls, data, **kwargs)

