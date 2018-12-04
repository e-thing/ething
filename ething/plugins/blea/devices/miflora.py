# coding: utf-8

from .. import process_mode
from ..BleaDevice import BleaDevice
from ething.core.reg import *
from ething.core.interfaces import Thermometer, LightSensor, MoistureSensor
from ething.core import scheduler


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

    @scheduler.setInterval(READ_INTERVAL, thread=process_mode, name="blea.miflora.read")
    def read(self):

        try:
            with self.connect() as connector:

                batteryFirmData = bytearray(connector.read_handle(0x38)) # read version & battery
                battery = batteryFirmData[0]
                firmware = "".join([chr(c) for c in batteryFirmData[2:]])

                self.log.debug('read battery:%s firmware:%s' % (battery, firmware))

                with self:
                    self.setConnectState(True)
                    self.firmware = firmware
                    self.battery = battery

                connector.write_handle(0x33, bytearray([0xA0, 0x1F]))  # change into write mode
                connector.wait_for_notification(0x36, self, notification_timeout=5)

        except Exception:
            self.log.exception('error in read()')
            self.setConnectState(False)

    def handleNotification(self,handle,data):
        if handle == 0x35:
            received = bytearray(data)
            temperature = float(received[1] * 256 + received[0]) / 10
            sunlight = received[4] * 256 + received[3]
            moisture = received[7]
            fertility = received[9] * 256 + received[8]

            self.log.debug('read temperature:%s sunlight:%s moisture:%s fertility:%s' % (temperature, sunlight, moisture, fertility))

            with self:
                self.temperature = temperature
                self.light_level = sunlight
                self.moisture = sunlight

                self.data.update({
                    'sunlight': sunlight,
                    'moisture': moisture,
                    'fertility': fertility,
                    'temperature': temperature
                })
        else:
            self.log.debug('unknown handle %X' % handle)
