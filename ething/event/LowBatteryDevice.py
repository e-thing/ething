# coding: utf-8

from .ResourceEvent import ResourceSignal, ResourceEvent, isResourceFilter, attr, isNone


class LowBatteryDevice(ResourceSignal):
    pass


@attr('resource', validator=isResourceFilter(onlyTypes=('Device',)) | isNone())
class LowBatteryDeviceEvent(ResourceEvent):
    """
    is emitted each time the device's battery level go under 10%
    """
    signal = LowBatteryDevice
