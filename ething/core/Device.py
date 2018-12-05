# coding: utf-8
from future.utils import string_types, integer_types, with_metaclass, listvalues
from .Resource import Resource
from .reg import *
from .rule.event import ResourceEvent, ResourceSignal
import datetime


class BatteryLevelChanged(ResourceSignal):
    def __init__(self, resource, new_value, old_value):
        super(BatteryLevelChanged, self).__init__(resource)
        self.new_value = new_value
        self.old_value = old_value


@attr('last_state', mode=PRIVATE, default=False)
@attr('repeat', type=Boolean(), default=False)
@attr('threshold', type=Number(), default=0)
@attr('trigger_mode', type=Enum((None, 'above threshold', 'below threshold', 'equal to')), default=None)
class BatteryLevelChangedEvent(ResourceEvent):
    """
    is emitted each time the battery level changed
    """
    signal = BatteryLevelChanged

    def _filter(self, signal, core, rule):
        if super(BatteryLevelChangedEvent, self)._filter(signal, core, rule):

            new_value = signal.new_value
            old_value = signal.old_value
            result = False

            try:
                trigger_mode = self.trigger_mode
                threshold = self.threshold

                if trigger_mode is None:
                    result = True
                elif trigger_mode == 'above threshold':
                    result = new_value >= threshold and old_value < threshold
                elif trigger_mode == 'below threshold':
                    result = new_value <= threshold and old_value > threshold
                elif trigger_mode == 'equal to':
                    result = new_value == threshold
            except Exception:
                pass

            last_state = self.last_state
            self.last_state = result

            if result:
                if not self.repeat:
                    if last_state:
                        result = False

            return result


class DeviceConnected(ResourceSignal):
    pass


class DeviceConnectedEvent(ResourceEvent):
    """
    is emitted each time a device connect
    """
    signal = DeviceConnected


class DeviceDisconnected(ResourceSignal):
    pass


class DeviceDisconnectedEvent(ResourceEvent):
    """
    is emitted each time a device disconnect
    """
    signal = DeviceDisconnected


@abstract
@throw(BatteryLevelChanged, DeviceConnected, DeviceDisconnected)
# 0-100 : the battery level, if None it means that no battery information is provided
@attr('battery', type=Nullable(Number(min=0, max=100)), default=None, watch=True, description="The battery level of this device (must be between 0 (empty) and 100 (full) , or null if the device has no battery information).")
@attr('location', type=String(), default='', description="The location of this device.")
@attr('connected', type=Boolean(), default=True, watch=True, description="Set to true when this device is connected.")
@attr('lastSeenDate', mode=READ_ONLY, default=None, description="The last time this device was reached or made a request.")
@attr('methods', default=lambda cls: [m.name for m in list_registered_methods(cls)], mode=READ_ONLY, description="The list of the methods available.")
class Device(Resource):

    BATTERY_NONE = None
    BATTERY_EMPTY = 0
    BATTERY_LOW = 10
    BATTERY_HALF = 50
    BATTERY_FULL = 100

    def setConnectState(self, connected):

        with self:
            connected = bool(connected)

            if connected:
                self.lastSeenDate = datetime.datetime.utcnow()

            if self.connected != connected:
                self.connected = connected

    def _watch(self, attr, new_value, old_value):
        super(Device, self)._watch(attr, new_value, old_value)

        if attr == 'battery':
            if new_value != old_value:
                self.dispatchSignal(BatteryLevelChanged(self, new_value, old_value))
        elif attr == 'connected':
            if new_value != old_value:
                if new_value:
                    self.log.debug("device connected %s" % self)
                    self.dispatchSignal(DeviceConnected(self))
                else:
                    self.log.debug("device disconnected %s" % self)
                    self.dispatchSignal(DeviceDisconnected(self))

    @classmethod
    def unserialize(cls, data, context = None):
        if data['location'] is None:
            data['location'] = ''
        return super(Device, cls).unserialize(data, context)
