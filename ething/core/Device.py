# coding: utf-8
from .Resource import Resource, ResourceType
from .utils.date import TzDate, utcnow
from .reg import *
from .Signal import ResourceSignal
from .flow import ResourceNode


@namespace('devices', True)
@meta(icon='mdi-battery-50')
class BatteryLevelChanged(ResourceSignal):
    """
    is emitted each time the battery level changed
    """
    def __init__(self, resource, new_value, old_value):
        super(BatteryLevelChanged, self).__init__(resource)
        self.payload = {
            'battery': new_value,
            'battery_old': old_value
        }


@namespace('devices', True)
@meta(icon='mdi-lan-connect')
class DeviceConnected(ResourceSignal):
    """
    is emitted each time a device connect
    """
    pass


@namespace('devices', True)
@meta(icon='mdi-lan-disconnect')
class DeviceDisconnected(ResourceSignal):
    """
    is emitted each time a device disconnect
    """
    pass


@meta(icon='mdi-play', category='function')
@attr('args', type=Dict(allow_extra = True), default={}, description="The arguments passed to the method")
@attr('method', type=String(), description="The method name")
@attr('resource', type=ResourceType(accepted_types=('resources/Device',)), description="The device on which the action is executed")
class ExecuteDevice(ResourceNode):
    INPUTS = ['default']
    OUTPUTS = ['default']

    def main(self, **inputs):
        device = self.resource

        if device is None:
            raise Exception("the device has been removed")

        res = getattr(device, self.method)(**self.args)

        self.emit({
            'payload': res
        })


@abstract
@throw(BatteryLevelChanged, DeviceConnected, DeviceDisconnected)
# 0-100 : the battery level, if None it means that no battery information is provided
@attr('battery', type=Nullable(Number(min=0, max=100)), default=None, description="The battery level of this device (must be between 0 (empty) and 100 (full) , or null if the device has no battery information).")
@attr('location', type=String(), default='', description="The location of this device.")
@attr('connected', type=Boolean(), default=True, description="Set to true when this device is connected.")
@attr('lastSeenDate', type=Nullable(TzDate()), mode=READ_ONLY, default=None, description="The last time this device was reached or made a request.")
@attr('error', type=Nullable(String()), mode=READ_ONLY, default=None, description="Any error concerning this device.")
class Device(Resource):

    """
    The base class of any device (Switch, light, sensor, controller, ...).


    To register a new Device, simply override the Device class ::

        # optional, for icons naming convention, see https://quasar-framework.org/components/icons.html
        @meta(icon='mdi-play', category='foo')
        # use the `attr` decorator to declare some specific attributes. If history is True, the values are stored in a table. If force_watch is False or not set, only values that differs from the previous one are stored.
        @attr('sensor_value', type=Number(), default=0, mode=READ_ONLY, history=True, force_watch=True, description="sensor value")
        class Foo(Device):

            # (optional) bind some method to the core.scheduler
            @setInterval(30)
            def read(self):
                # this method will be called every 30 seconds during all the lifetime of this instance.
                this.sensor_value = self._read_value_from_the_sensor()

            @method # register this method
            def do_something(self):
                pass


    .. note::
        The registered attributes (using `@attr`) and methods (using `@method`) will be automatically available in the web interface.

    .. note::
        For generic device (sensor, switch, camera, ...) see the interfaces module which list all generic devices.

    """

    BATTERY_NONE = None
    BATTERY_EMPTY = 0
    BATTERY_LOW = 10
    BATTERY_HALF = 50
    BATTERY_FULL = 100

    def setConnectState(self, connected):

        with self:
            connected = bool(connected)

            if connected:
                self.lastSeenDate = utcnow()

            if self.connected != connected:
                self.connected = connected

    def on_attr_update(self, attr, new_value, old_value):
        super(Device, self).on_attr_update(attr, new_value, old_value)

        if attr == 'battery':
            self.dispatchSignal(BatteryLevelChanged(self, new_value, old_value))
        elif attr == 'connected':
            if new_value:
                self.log.debug("device connected %s" % self)
                self.dispatchSignal(DeviceConnected(self))
            else:
                self.log.debug("device disconnected %s" % self)
                self.dispatchSignal(DeviceDisconnected(self))
        elif attr == 'error':
            if new_value is not None:
                self.log.error(new_value)
