# coding: utf-8

from ...entity import *
import logging


def _attr_signal_default(cls):
    if cls.signal is not None:
        return cls.signal.__name__
    else:
        return None


@path('events')
@abstract
@attr('type', mode=READ_ONLY, default=lambda cls: str(cls.__name__), description="The type of the event")
@attr('signal', mode=READ_ONLY, default=_attr_signal_default, description="The name of the signals this event is listening to")
class Event(Entity):

    signal = None

    @property
    def log(self):
        return logging.getLogger('ething.%s' % self.type)

    @property
    def rule(self):
        return self.get_root()

    @property
    def ething(self):
        return self.rule.ething

    def filter(self, signal):

        if not isinstance(signal, type(self).signal):
            return False

        try:
            return self._filter(signal)
        except:
            self.ething.log.exception('error in event filter for : %s' % self)
            return False

    def _filter(self, signal):
        return True

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

    @classmethod
    def toSchema(cls, **kwargs):
        schema = Entity.toSchema.__func__(cls, **kwargs)
        if cls.signal:
            schema['signal'] = cls.signal.__name__
        return schema