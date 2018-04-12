# coding: utf-8


from . import ResourceSignal, ResourceEvent


class ResourceCreated(ResourceSignal):
    pass


class ResourceCreatedEvent(ResourceEvent):
    signal = ResourceCreated
    


