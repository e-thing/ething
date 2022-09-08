# coding: utf-8
from ething.Device import *
from ething.plugin import Plugin
from ething.scheduler import set_interval, at
from ething.interfaces.powerMeter import PowerMeter
from ething.interfaces.sensor import sensor_attr

import struct
import serial
import minimalmodbus
import time




class Orno(Plugin):
    # the path of your Javascript index file, this file describe how your plugin should be integrated into the web interface.
    # remove it if not used
    JS_INDEX = './index.js'

    # this method is executed once, after the core instance is initialized (database, ...)
    def setup(self):
        pass


#
# see https://github.com/gituser-rk/orno-modbus-mqtt/blob/master/modbus-mqtt.py
#
@attr('serial_port', type=SerialPort(), description="The serial port the device is connected to.")
@attr('device_id', type=Number(min=1, max=255), default=1, description="The serial port the device is connected to.")
@sensor_attr('frequency', type=Number(), default=0, unit="Hz", description = "Frequency in Hz.")
@sensor_attr('voltage', type=Number(), default=0, unit="V", description = "Voltage in V")
@sensor_attr('current', type=Number(), default=0, unit="A", description = "Current in A")
@sensor_attr('reactive_power', type=Number(), default=0, unit="Var", description = "ReactivePower in Var")
@sensor_attr('apparent_power', type=Number(), default=0, unit="VA", description = "ApparentPower in VA")
@sensor_attr('power_factor', type=Number(), default=0, history=False, description = "PowerFactor")
@sensor_attr('active_energy', type=Number(), default=0, unit="kWh", history=False, description = "ActiveEnergy in kWh")
@sensor_attr('reactive_energy', type=Number(), default=0, unit="kvarh", history=False, description = "ReactiveEnergy in kvarh")
@attr('last_hourly_index', mode=PRIVATE, default=None)
@attr('last_hourly_ts', mode=PRIVATE, default=None)
@attr('last_daily_index', mode=PRIVATE, default=None)
@attr('last_daily_ts', mode=PRIVATE, default=None)
class Orno_WE_514 (PowerMeter):
    """
    Orno-WE-514 device connected to a rs485 to usb-serial converter.
    """
    def __init__(self, *args, **kwargs):
        super(Orno_WE_514, self).__init__(*args, **kwargs)
        self._mmi = None
        self._configure()

    def _configure(self):

        if self._mmi is not None:
            # close
            self._mmi = None

        if self.serial_port:
            self._mmi = minimalmodbus.Instrument(self.serial_port, self.device_id)
            self._mmi.serial.baudrate = 9600         # Baud
            self._mmi.serial.bytesize = 8
            self._mmi.serial.parity   = serial.PARITY_NONE # vendor default is EVEN
            self._mmi.serial.stopbits = 1
            self._mmi.serial.timeout  = 0.10          # seconds
            self._mmi.mode = minimalmodbus.MODE_RTU   # rtu or ascii mode
            self._mmi.clear_buffers_before_each_transaction = True
            self._mmi.debug = False # set to "True" for debug mode

    def on_attr_update(self, attr, new_value, old_value):
        super(Orno_WE_514, self).on_attr_update(attr, new_value, old_value)
        if attr == 'serial_port' or attr == 'device_id':
            self._configure()

    @set_interval(10)
    def refresh(self):
        if self._mmi is not None:
            with self:
                try:
                    Frequency = self._mmi.read_register(304, 2, 3, True)  # registeraddress, number_of_decimals=0, functioncode=3, signed=False
                    self.frequency = Frequency # publish Frequency in Hz
                    Voltage = self._mmi.read_register(305, 2, 3, True)
                    self.voltage = Voltage # publish Voltage in V
                    Current = self._mmi.read_long(313, 3, False, 0) #registeraddress, functioncode=3, signed=False, byteorder=0) in mA
                    Current = Current/1000 # convert mA to A
                    self.current = Current # publish Current in A
                    ActivePower = self._mmi.read_long(320, 3, False, 0) #registeraddress, functioncode=3, signed=False, byteorder=0)
                    self.power = ActivePower # publish ActivePower in W
                    ReactivePower =  self._mmi.read_long(328, 3, False, 0) #registeraddress, functioncode=3, signed=False, byteorder=0)
                    self.reactive_power = ReactivePower # publish ReactivePower in Var
                    ApparentPower = self._mmi.read_long(336, 3, False, 0) #registeraddress, functioncode=3, signed=False, byteorder=0)
                    self.apparent_power = ApparentPower # publish ApparentPower in VA
                    PowerFactor = self._mmi.read_register(344, 3, 3, True)
                    self.power_factor = PowerFactor # publish PowerFactor
                    ActiveEnergy = self._mmi.read_registers(40960, 10, 3) #read_registers(registeraddress, number_of_registers, functioncode=3)
                    bits = (ActiveEnergy[0] << 16) + ActiveEnergy[1] # combining Total Energy valuepair
                    s = struct.pack('>i', bits) # write to string an interpret as int
                    tmp = struct.unpack('>L', s)[0] # extract from string and interpret as unsigned long
                    tmpFloat1 = tmp/100 # needs to be converted
                    self.active_energy = float(tmpFloat1) # publish ActiveEnergy in kWh
                    ReactiveEnergy = self._mmi.read_registers(40990, 10, 3) #read_registers(registeraddress, number_of_registers, functioncode=3)
                    bits = (ReactiveEnergy[0] << 16) + ReactiveEnergy[1] # combining Total Energy valuepair
                    s = struct.pack('>i', bits) # write to string an interpret as int
                    tmp = struct.unpack('>L', s)[0] # extract from string and interpret as unsigned long
                    tmpFloat2 = tmp/100 # needs to be converted
                    self.reactive_energy = float(tmpFloat2) # publish ReactiveEnergy in kvarh

                    self.refresh_connect_state(True)
                except IOError:
                    self.refresh_connect_state(False)

    @at(hour='*', min=0)
    def _hourly(self):
        current = self.active_energy
        last = self.last_hourly_index

        if last is not None:
            delay = time.time() - self.last_hourly_ts
            if delay < (3600 + 120) and delay > (3600 - 120):
                consumption = current - last
                # add it to the table
                self.store("consumption_hourly", consumption, name="value")

        with self:
            self.last_hourly_index = current
            self.last_hourly_ts = time.time()

    @at(hour=0, min=0)
    def _daily(self):
        current = self.active_energy
        last = self.last_daily_index

        if last is not None:
            delay = time.time() - self.last_daily_ts
            if delay < (86400 + 120) and delay > (86400 - 120):
                consumption = current - last
                # add it to the table
                self.store("consumption_daily", consumption, name="value")

        with self:
            self.last_daily_index = current
            self.last_daily_ts = time.time()



