# coding: utf-8

from ething.meta import MetaAction, get_action_class
from future.utils import with_metaclass, string_types
from ething.base import DataObject, attr, READ_ONLY, abstract


def _attr_signal_default(cls):
    if cls.signal is not None:
        return cls.signal.__name__
    else:
        return None


@abstract
@attr('type', mode=READ_ONLY, default=lambda cls: str(cls.__name__), description="The type of the action")
class Action(with_metaclass(MetaAction, DataObject)):

    def __init__(self, parent, data=None):
        object.__setattr__(self, '_Action__rule', parent)
        super(Action, self).__init__(data=data)

    @property
    def rule(self):
        return self.__rule

    @property
    def ething(self):
        return self.rule.ething

    def run(self, signal):
        raise NotImplementedError()

    @classmethod
    def unserialize(cls, data, **ctor_attr):
        type = data.get('type')
        _cls = get_action_class(type)
        return _cls(data=data, **ctor_attr)

    @classmethod
    def create(cls, attributes, **ctor_attr):

        if cls == Action:
            type = attributes.get('type')

            if not isinstance(type, string_types) or len(type) == 0:
                raise ValueError(
                    'the "type" attribute of the Action class is mandatory and must be a non empty string')

            _cls = get_action_class(type)
            if _cls is None:
                raise ValueError('the action class "%s" does not exist' % type)

            # remove 'type' attribute
            cpy = attributes.copy()
            cpy.pop('type')
            attributes = cpy

        return DataObject.create.__func__(_cls, attributes, **ctor_attr)

    def _insert(self, data):
        pass

    def _save(self, data):
        pass

    def _refresh(self):
        return self.__d

