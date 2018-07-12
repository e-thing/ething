# coding: utf-8
from future.utils import integer_types
from .ResourceEvent import ResourceSignal, ResourceEvent, isResourceFilter, attr, isNone
from ething.base import isString, isEnum, isNumber, isBool, PRIVATE

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


@attr('repeat', validator=isBool(), default=False, description="If true, the rule will be triggered each time the value match the threshold condition. Else the rule is triggered only the first time the threshold condition is met, then the rule is disabled until the threshold condition is not met.")
@attr('threshold_value', validator=isNumber())
@attr('threshold_mode', validator=isEnum(('gt', 'ge', 'lt', 'le')))
@attr('key', validator=isString(allow_empty = False), description="The name of the column in the table")
@attr('resource', validator=isResourceFilter(onlyTypes=('Table',)))
@attr('last_status', mode=PRIVATE, default=False)
class TableDataThresholdEvent(ResourceEvent):
    """
    is emitted each time a value is appended to a table is over or below a threshold
    """
    signal = TableDataAdded

    def _filter(self, signal):
        ret = False

        if super(TableDataThresholdEvent, self)._filter(signal):
            key = self.key

            if key in signal.data:
                value = signal.data.get(key)

                if isinstance(value, integer_types) or isinstance(value, float):
                    threshold_mode = self.threshold_mode
                    threshold_value = self.threshold_value

                    if threshold_mode == 'gt':
                        if value > threshold_value:
                            ret = True
                    elif threshold_mode == 'ge':
                        if value >= threshold_value:
                            ret = True
                    elif threshold_mode == 'lt':
                        if value < threshold_value:
                            ret = True
                    elif threshold_mode == 'le':
                        if value <= threshold_value:
                            ret = True

                last_status = self._last_status
                self._last_status = ret

                if not self.repeat and ret and last_status:
                    ret = False

        return ret
