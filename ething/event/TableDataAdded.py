# coding: utf-8
from future.utils import integer_types
from .ResourceEvent import ResourceSignal, ResourceEvent, isResourceFilter, attr, isNone
from ething.base import isString, isEnum, isNumber

class TableDataAdded(ResourceSignal):
    def __init__(self, resource, data):
        super(TableDataAdded, self).__init__(resource)
        self.data = data


@attr('resource', validator=isResourceFilter(onlyTypes=('Table',)) | isNone())
class TableDataAddedEvent(ResourceEvent):
    """
    is emitted each time a new value is appended to a table
    """
    signal = TableDataAdded


@attr('threshold_value', validator=isNumber())
@attr('threshold_mode', validator=isEnum(('gt', 'ge', 'lt', 'le')))
@attr('key', validator=isString(allow_empty = False))
@attr('resource', validator=isResourceFilter(onlyTypes=('Table',)))
class TableDataThresholdEvent(ResourceEvent):
    """
    is emitted each time a value is appended to a table is over or below a threshold
    """
    signal = TableDataAdded

    def _filter(self, signal):

        if super(TableDataThresholdEvent, self)._filter(signal):
            key = self.key

            if key in signal.data:
                value = signal.data.get(key)

                if isinstance(value, integer_types) or isinstance(value, float):
                    threshold_mode = self.threshold_mode
                    threshold_value = self.threshold_value

                    if threshold_mode == 'gt':
                        if value > threshold_value:
                            return True
                    elif threshold_mode == 'ge':
                        if value >= threshold_value:
                            return True
                    elif threshold_mode == 'lt':
                        if value < threshold_value:
                            return True
                    elif threshold_mode == 'le':
                        if value <= threshold_value:
                            return True

        return False
