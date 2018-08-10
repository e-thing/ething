# coding: utf-8

from .ResourceEvent import ResourceSignal, ResourceEvent, ResourceFilter, attr


class LowBatteryDevice(ResourceSignal):
    pass


@attr('resource', type=ResourceFilter(onlyTypes=('resources/Device',)))
class LowBatteryDeviceEvent(ResourceEvent):
    """
    is emitted each time the device's battery level go under 10%
    """
    signal = LowBatteryDevice
