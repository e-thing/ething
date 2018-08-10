# coding: utf-8

from .ResourceEvent import ResourceSignal, ResourceEvent, ResourceFilter, attr


class DeviceConnected(ResourceSignal):
    pass


@attr('resource', type=ResourceFilter(onlyTypes=('resources/Device',)))
class DeviceConnectedEvent(ResourceEvent):
    """
    is emitted each time a device connect
    """
    signal = DeviceConnected
