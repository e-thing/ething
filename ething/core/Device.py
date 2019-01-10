# coding: utf-8
from future.utils import string_types, integer_types, with_metaclass, listvalues
from .Resource import Resource
from .date import TzDate, utcnow
from .reg import *
from .rule.event import ResourceEvent, ResourceSignal, ResourceFilter


class BatteryLevelChanged(ResourceSignal):
    def __init__(self, resource, new_value, old_value):
        super(BatteryLevelChanged, self).__init__(resource)
        self.battery = new_value


@path('devices', True)
@meta(icon='mdi-battery-50')
@attr('resource', type=ResourceFilter(must_throw=BatteryLevelChanged))
class BatteryLevelChangedEvent(ResourceEvent):
    """
    is emitted each time the battery level changed
    """
    signal = BatteryLevelChanged


class DeviceConnected(ResourceSignal):
    pass


@path('devices', True)
@meta(icon='mdi-lan-connect')
@attr('resource', type=ResourceFilter(must_throw=DeviceConnected))
class DeviceConnectedEvent(ResourceEvent):
    """
    is emitted each time a device connect
    """
    signal = DeviceConnected


class DeviceDisconnected(ResourceSignal):
    pass


@path('devices', True)
@meta(icon='mdi-lan-disconnect')
@attr('resource', type=ResourceFilter(must_throw=DeviceDisconnected))
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
@attr('lastSeenDate', type=Nullable(TzDate()), mode=READ_ONLY, default=None, description="The last time this device was reached or made a request.")
class Device(Resource):

    BATTERY_NONE = None
    BATTERY_EMPTY = 0
    BATTERY_LOW = 10
    BATTERY_HALF = 50
    BATTERY_FULL = 100

    @attr(description="The list of the methods available.")
    def methods(self):
        return [m.name for m in list_registered_methods(self)]

    def setConnectState(self, connected):

        with self:
            connected = bool(connected)

            if connected:
                self.lastSeenDate = utcnow()

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
