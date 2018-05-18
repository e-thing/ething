# coding: utf-8

from .ResourceEvent import ResourceSignal, ResourceEvent, isResourceFilter, attr, isNone


class DeviceConnected(ResourceSignal):
    pass


@attr('resource', validator = isResourceFilter(onlyTypes = ('Device',)) | isNone())
class DeviceConnectedEvent(ResourceEvent):
    """
    is emitted each time a device connect
    """
    signal = DeviceConnected
    