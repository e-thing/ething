# coding: utf-8


from . import ResourceSignal, ResourceEvent


class ResourceDeleted(ResourceSignal):
    pass


class ResourceDeletedEvent(ResourceEvent):
    signal = ResourceDeleted
    