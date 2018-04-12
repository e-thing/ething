# coding: utf-8

from .ResourceEvent import ResourceSignal, ResourceEvent, isResourceFilter, attr, isNone


class LowBatteryDevice(ResourceSignal):
    pass


@attr('resource', validator = isResourceFilter(onlyTypes = ('Device',)) | isNone())
class LowBatteryDeviceEvent(ResourceEvent):
    signal = LowBatteryDevice
    