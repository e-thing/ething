# coding: utf-8


from . import ResourceSignal, ResourceEvent
from ething.reg import *


class ResourceMetaUpdated(ResourceSignal):

    def __init__(self, resource, attributes):
        super(ResourceMetaUpdated, self).__init__(resource)
        self.attributes = attributes


@attr('attributes', type=Nullable(Array(min_len=1, item=String(allow_empty=False))), default=None)
class ResourceMetaUpdatedEvent(ResourceEvent):
    """
    is emitted each time a resource attribute has been updated
    """

    signal = ResourceMetaUpdated

    def _filter(self, signal):

        if super(ResourceMetaUpdatedEvent, self)._filter(signal):
            a = self.attributes

            if not a:
                return True

            b = signal.attributes
            for val in a:
                if val in b:
                    return True

        return False
