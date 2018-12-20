# coding: utf-8

from ...entity import *
import logging


@path('conditions')
@abstract
@attr('type', mode=READ_ONLY, default=lambda cls: str(cls.__name__), description="The type of the action")
class Condition(Entity):

    @property
    def log(self):
        return logging.getLogger('ething.%s' % self.type)

    def test(self, signal, core):
        raise NotImplementedError()

    @classmethod
    def unserialize(cls, data, context = None):
        type = data.get('type')
        _cls = get_registered_class(type)
        if _cls is None:
            raise Exception('unknown type "%s"' % type)
        return Entity.unserialize.__func__(_cls, data, context)

    @classmethod
    def fromJson(cls, data, context = None):
        type = data.get('type')
        _cls = get_registered_class(type)
        if _cls is None:
            raise Exception('unknown type "%s"' % type)
        return Entity.fromJson.__func__(_cls, data, context)

