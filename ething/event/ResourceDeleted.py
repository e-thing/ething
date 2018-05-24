# coding: utf-8


from . import ResourceSignal, ResourceEvent


class ResourceDeleted(ResourceSignal):
    pass


class ResourceDeletedEvent(ResourceEvent):
    """
    is emitted each time a resource is deleted
    """
    signal = ResourceDeleted
