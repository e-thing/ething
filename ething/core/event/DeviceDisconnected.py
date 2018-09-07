# coding: utf-8

from .ResourceEvent import ResourceSignal, ResourceEvent, ResourceFilter, attr


class DeviceDisconnected(ResourceSignal):
    pass


@attr('resource', type=ResourceFilter(onlyTypes=('resources/Device',)))
class DeviceDisconnectedEvent(ResourceEvent):
    """
    is emitted each time a device disconnect
    """
    signal = DeviceDisconnected
