# coding: utf-8


from .ResourceEvent import ResourceSignal, ResourceEvent, isResourceFilter, attr, isNone


class DeviceDataSet(ResourceSignal):
    
    def __init__(self, resource, data):
        super(DeviceDataSet, self).__init__(resource)
        self.data = data


@attr('resource', validator = isResourceFilter(onlyTypes = ('Device',)) | isNone())
class DeviceDataSetEvent(ResourceEvent):
    """
    is emitted each time a device emitted data
    """
    signal = DeviceDataSet



