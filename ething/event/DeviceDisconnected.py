# coding: utf-8

from .ResourceEvent import ResourceSignal, ResourceEvent, isResourceFilter, attr, isNone


class DeviceDisconnected(ResourceSignal):
    pass


@attr('resource', validator = isResourceFilter(onlyTypes = ('Device',)) | isNone())
class DeviceDisconnectedEvent(ResourceEvent):
    """
    is emitted each time a device disconnect
    """
    signal = DeviceDisconnected
    