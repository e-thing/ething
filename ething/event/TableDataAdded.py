# coding: utf-8

from .ResourceEvent import ResourceSignal, ResourceEvent, isResourceFilter, attr, isNone


class TableDataAdded(ResourceSignal):
    def __init__(self, resource, data):
        super(TableDataAdded, self).__init__(resource)
        self.data = data


@attr('resource', validator = isResourceFilter(onlyTypes = ('Table',)) | isNone())
class TableDataAddedEvent(ResourceEvent):
    signal = TableDataAdded
