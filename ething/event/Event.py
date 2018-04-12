# coding: utf-8

from ething.meta import MetaEvent, get_event_class
from future.utils import with_metaclass, string_types
from ething.base import DataObject, attr, READ_ONLY


def _attr_signal_default(cls):
    if cls.signal is not None:
        if isinstance(cls.signal, list) or isinstance(cls.signal, tuple):
            return [s.__name__ for s in cls.signal]
        else:
            return [cls.signal.__name__]
    else:
        return None


@attr('type', mode = READ_ONLY, default = lambda cls: str(cls.__name__), description = "The type of the event")
@attr('signal', mode = READ_ONLY, default = _attr_signal_default, description = "The name of the signals this event is listening to")
class Event(with_metaclass(MetaEvent,DataObject)):
    
    signal = None
    
    
    def __init__ (self, ething, data = None):
        object.__setattr__(self, '_Event__ething', ething)
        super(Event, self).__init__(data = data)
    
    @property
    def ething (self):
        return self.__ething
    
    
    
    def filter(self, signal):
        
        if self.signal is not None:
            if isinstance(self.signal, list) or isinstance(self.signal, tuple):
                if type(signal) not in self.signal:
                    return False
            elif not isinstance(signal, self.signal):
                return False
        
        return self._filter(signal)
        
    
    def _filter(self, signal):
        return True
    
    @classmethod
    def unserialize(cls, data, **ctor_attr):
        type = data.get('type')
        event_cls = get_event_class(type)
        return event_cls(data = data, **ctor_attr)
    
    @classmethod
    def create(cls, attributes, **ctor_attr):
        
        if cls == Event:
            type = attributes.get('type')
            
            if not isinstance(type, string_types) or len(type)==0:
                raise ValueError('the "type" attribute of the Event class is mandatory and must be a non empty string')
            
            cls = get_event_class(type)
            if cls is None:
                raise ValueError('the event class "%s" does not exist' % type)
            
            # remove 'type' attribute
            cpy = attributes.copy()
            cpy.pop('type')
            attributes = cpy
        
        return DataObject.create.__func__(cls, attributes, **ctor_attr)
    
    def _insert(self, data):
        pass
    
    def _save(self, data):
        pass
    
    def _refresh(self):
        return self.__d

