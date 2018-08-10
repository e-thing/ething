# coding: utf-8
from future.utils import string_types, integer_types

from future.utils import with_metaclass, listvalues
from ething.Resource import Resource
from .reg import *
import datetime


def on_battery_change(self, value, old_value):
    if value < self.BATTERY_LOW:
        if old_value >= self.BATTERY_LOW:
            self.dispatchSignal('LowBatteryDevice', self)


@abstract
# 0-100 : the battery level, if None it means that no battery information is provided
@attr('battery', type=Nullable(Integer(min=0, max=100)), default=None, on_change=on_battery_change, description="The battery level of this device (must be between 0 (empty) and 100 (full) , or null if the device has no battery information).")
@attr('location', type=Nullable(String()), default=None, description="The location of this device.")
@attr('connected', type=Boolean(), default=True, description="Set to true when this device is connected.")
@attr('lastSeenDate', mode=READ_ONLY, default=None, description="The last time this device was reached or made a request.")
@attr('methods', default=[], mode=READ_ONLY, description="The list of the methods available.")
@attr('interfaces', default=[], mode=READ_ONLY, description="A list of interfaces this device inherit")
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
                self._lastSeenDate = datetime.datetime.utcnow()

            if self.connected != connected:
                self.connected = connected

                if connected:
                    self.ething.log.debug("device connected %s" % self)
                    self.dispatchSignal('DeviceConnected', self)
                else:
                    self.ething.log.debug("device disconnected %s" % self)
                    self.dispatchSignal('DeviceDisconnected', self)

