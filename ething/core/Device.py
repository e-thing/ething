# coding: utf-8
from .Resource import Resource, ResourceType
from .date import TzDate, utcnow
from .reg import *
from .Signal import ResourceSignal
from .Flow import ResourceActionNode


@path('devices', True)
@meta(icon='mdi-battery-50')
class BatteryLevelChanged(ResourceSignal):
    """
    is emitted each time the battery level changed
    """
    def __init__(self, resource, new_value, old_value):
        super(BatteryLevelChanged, self).__init__(resource)
        self.battery = new_value


@path('devices', True)
@meta(icon='mdi-lan-connect')
class DeviceConnected(ResourceSignal):
    """
    is emitted each time a device connect
    """
    pass


@path('devices', True)
@meta(icon='mdi-lan-disconnect')
class DeviceDisconnected(ResourceSignal):
    """
    is emitted each time a device disconnect
    """
    pass


@attr('args', type=Dict(allow_extra = True), default={}, description="The arguments passed to the method")
@attr('method', type=String(), description="The method name")
@attr('resource', type=ResourceType(accepted_types=('resources/Device',)), description="The device on which the action is executed")
class ExecuteDevice(ResourceActionNode):
    def run(self, signal, core):
        device = core.get(self.resource)

        if device is None:
            raise Exception("the device has been removed")

        device.interface.call(self.method, **self.args)


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
