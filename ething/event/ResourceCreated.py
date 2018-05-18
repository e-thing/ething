# coding: utf-8


from . import ResourceSignal, ResourceEvent


class ResourceCreated(ResourceSignal):
    pass


class ResourceCreatedEvent(ResourceEvent):
    """
    is emitted each time a resource is created
    """
    signal = ResourceCreated
    


