# coding: utf-8


from .ResourceEvent import ResourceSignal, ResourceEvent, ResourceFilter, attr


class DeviceDataSet(ResourceSignal):

    def __init__(self, resource, data):
        super(DeviceDataSet, self).__init__(resource)
        self.data = data


@attr('resource', type=ResourceFilter(onlyTypes=('resources/Device',)))
class DeviceDataSetEvent(ResourceEvent):
    """
    is emitted each time a device emitted data
    """
    signal = DeviceDataSet
