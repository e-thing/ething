# coding: utf-8

from ..BleaDevice import BleaDevice
from ething.core.reg import *
from ething.core.interfaces import Thermometer, LightSensor, MoistureSensor
from ething.core import scheduler
from ething.core.Process import ThreadProcess # do not use GreenProcess since bluepy use select (blocking and not patchable)


VALID_DEVICE_NAMES = ['flower mate',
                      'flower care']

DEVICE_PREFIX = 'C4:7C:8D:'

READ_INTERVAL = 300


@attr('firmware', default='unknown', mode=READ_ONLY, description="The firmware version of this device.")
class Miflora(BleaDevice, Thermometer, LightSensor, MoistureSensor):
    
    name = 'miflora'
    
    @classmethod
    def isvalid(cls, name, mac, manufacturer):
        if (name is not None and name.lower() in VALID_DEVICE_NAMES) or (mac is not None and mac.upper().startswith(DEVICE_PREFIX)):
            return True

    @scheduler.setInterval(READ_INTERVAL, thread=ThreadProcess, name="blea.miflora.read")
    def read(self):

        batteryFirmData = None
        rawData = None

        try:
            with self.connect() as connector:

                batteryFirmData = bytearray(connector.read_handle('0x38')) # read version & battery
                battery = batteryFirmData[0]
                firmware = "".join([chr(c) for c in batteryFirmData[2:]])

                self.log.debug('read battery:%s firmware:%s' % (battery, firmware))

                with self:
                    self.firmware = firmware
                    self.battery = battery
                    self.setConnectState(True)

                if firmware >= "2.6.6":
                    # for the newer models a magic number must be written before we can read the current data
                    connector.write_handle('0x33', 'a01f')  # change into write mode

                rawData = bytearray(connector.read_handle('0x35'))  # read data

        except Exception:
            self.log.exception('error in read()')
            self.setConnectState(False)
        finally:

            with self:
                self.setConnectState(batteryFirmData is not None or rawData is not None)

                if batteryFirmData is not None:
                    self.firmware = firmware
                    self.battery = battery

                if rawData is not None:
                    temperature = float(rawData[1] * 256 + rawData[0]) / 10
                    sunlight = rawData[4] * 256 + rawData[3]
                    moisture = rawData[7]
                    fertility = rawData[9] * 256 + rawData[8]

                    self.log.debug('read data:%s temperature:%s sunlight:%s moisture:%s fertility:%s' % (rawData, temperature, sunlight, moisture, fertility))

                    self.temperature = temperature
                    self.light_level = sunlight
                    self.moisture = sunlight

                    self.data.update({
                        'sunlight': sunlight,
                        'moisture': moisture,
                        'fertility': fertility,
                        'temperature': temperature
                    })

