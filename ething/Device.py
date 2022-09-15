# coding: utf-8
from .Resource import Resource, ResourceType
from .utils.date import TzDate, utcnow
from .reg import *
from .Signal import ResourceSignal
from .flow import ResourceNode, Descriptor
from .env import get_options




@meta(icon='mdi-battery-alert')
class BatteryLevelLow(ResourceSignal):
    """
    is emitted when the battery level goes below 30%
    """

    def __init__(self, resource, new_value):
        super(BatteryLevelLow, self).__init__(resource, battery=new_value)


@meta(icon='mdi-lan-connect')
class DeviceConnected(ResourceSignal):
    """
    is emitted each time a device connect
    """
    pass


@meta(icon='mdi-lan-disconnect')
class DeviceDisconnected(ResourceSignal):
    """
    is emitted each time a device disconnect
    """
    pass


@meta(icon='mdi-play', category='function', label="Run device command")
@attr('args', type=Dict(allow_extra=True), default={}, description="The arguments passed to the method")
@attr('method', type=String(), description="The method name")
@attr('resource', type=ResourceType(accepted_types=('resources/Device',)),
      description="The device on which the action is executed")
class ExecuteDevice(ResourceNode):
    """
    Run a command of a device.
    """
    INPUTS = ['default']
    OUTPUTS = ['default']

    def main(self, **inputs):
        device = self.resource

        if device is None:
            raise Exception("the device has been removed")

        # get arguments
        _msg = inputs['default']
        _context = {
            'msg': _msg,
            'flow': self.flow
        }

        true_args = dict()

        for k in self.args:
            arg = self.args[k]
            type = arg['type'] # msg, glob ... or value
            value = arg['value'] # the actual value

            if type == 'value':
                # no transformation needed
                true_args[k] = value
            else:
                true_args[k] = Descriptor.parse_value(type, value, **_context)

        res = getattr(device, self.method)(**true_args)

        self.emit({
            'payload': res
        })


@abstract
@throw(BatteryLevelLow, DeviceConnected, DeviceDisconnected)
# 0-100 : the battery level, if None it means that no battery information is provided
@attr('battery', type=Nullable(Number(min=0, max=100)), mode=READ_ONLY, default=None,
      description="The battery level of this device (must be between 0 (empty) and 100 (full) , or null if the device has no battery information).")
@attr('rlink_quality', type=Nullable(Number(min=0, max=100)), mode=READ_ONLY, default=None,
      description="The signal quality level of this device (must be between 0 (too far) and 100 (excellent) , or null if the device is wired connected).")
@attr('location', type=String(), default='', description="The location of this device.")
# @attr('connected', type=Boolean(), default=True, mode=READ_ONLY, force_watch=True, description="Set to true when this device is connected.")
@attr('connected', type=Boolean(), default=True, mode=READ_ONLY,
      description="Set to true when this device is connected.")
@attr('lastSeenDate', type=Nullable(TzDate()), mode=READ_ONLY, default=None,
      description="The last time this device was reached or made a request.")
@attr('error', type=Nullable(String()), mode=READ_ONLY, default=None, description="Any error concerning this device.")
@meta(description='')
class Device(Resource):
    """
    The base class of any device (Switch, light, sensor, controller, ...).


    To register a new Device, simply override the Device class ::

        # optional, for icons naming convention, see https://quasar-framework.org/components/icons.html
        @meta(icon='mdi-play', category='foo')
        # use the `attr` decorator to declare some specific attributes. If history is True, the values are stored in a table. If force_watch is False or not set, only values that differs from the previous one are stored.
        @attr('sensor_value', type=Number(), default=0, mode=READ_ONLY, history=True, force_watch=True, description="sensor value")
        class Foo(Device):

            # (optional) bind some method to the scheduler
            @set_interval(30)
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

    ACTIVITY_TIMEOUT = None  # number of seconds after which the device is automatically detected as not connected

    # def __watch__(self, attr, value, old_value):
    #     if attr == 'connected' and value:
    #         self.lastSeenDate = utcnow()
    #     super(Device, self).__watch__(attr, value, old_value)

    def on_attr_update(self, attr, new_value, old_value):
        super(Device, self).on_attr_update(attr, new_value, old_value)

        if attr == 'battery':
            if new_value is not None:
                if new_value <= 30 and (old_value is None or old_value > 30):
                    self.emit(BatteryLevelLow(self, new_value))
        elif attr == 'connected':
            if new_value:
                self.logger.debug("device connected %s", self)
                self.emit(DeviceConnected(self))
            else:
                self.logger.debug("device disconnected %s", self)
                self.emit(DeviceDisconnected(self))
        elif attr == 'error':
            if new_value is not None:
                self.logger.error(new_value)

    def refresh_connect_state(self, state, propagate=True):
        with self:
            self.connected = bool(state)
            if state:
                self.lastSeenDate = utcnow()

        if not state and propagate:
            for dev in self.children(lambda r: r.typeof(Device)):
                dev.refresh_connect_state(state)

    def check_activity(self):
        if self.ACTIVITY_TIMEOUT and self.connected and utcnow() - self.lastSeenDate > datetime.timedelta(
                seconds=self.ACTIVITY_TIMEOUT):
            self.refresh_connect_state(False)

    def __db_save__(self, insert):
        super(Device, self).__db_save__(insert)
        if insert:
            self.notification.success('Device created: %s' % self.name, timeout=10)


@meta(icon='mdi-bluetooth')
@attr('rssi', mode=READ_ONLY, default=None, description="The last received signal strength indicator of this device.")
@attr('address', type=String(regex='^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$'),
      description='the address of the device')
@abstract
class BleDevice(Device):

    @property
    def hci(self):
        return int(get_options().get('ble_hci', 0))
