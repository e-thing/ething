# coding: utf-8

from ..BleaDevice import BleaDevice
from ething.core.interfaces import Thermometer, HumiditySensor
from ething.core import scheduler
import re


READ_INTERVAL = 300


class Mijia(BleaDevice, Thermometer, HumiditySensor):
    
    name = 'Mijia BT Hygrothermograph'
    
    @classmethod
    def isvalid(cls, name, mac, manufacturer):
        if name is not None and name.upper().startswith('MJ_HT_'):
            return True

    @scheduler.set_interval(READ_INTERVAL, name="blea.mijia.read")
    def read(self):

        try:
            with self.connect() as connector:
                batteryData = bytearray(connector.read_handle(0x18)) # battery
                battery = batteryData[0]

                self.log.debug('read battery:%s' % (battery))

                with self:
                    self.refresh_connect_state(True)
                    self.battery = battery

                connector.wait_for_notification(0x10, self, notification_timeout=5)

        except Exception:
            self.log.exception('error in read()')
            self.refresh_connect_state(False)

    def handleNotification(self,handle,data):
        if handle == 0x0e:
            m = re.search('T=([\d\.]*)\s+?H=([\d\.]*)', ''.join(map(chr, bytearray(data))))
            temperature = float(m.group(1))
            humidity = float(m.group(2))

            self.log.debug('read temperature:%s humidity:%s' % (temperature, humidity))

            with self:
                self.temperature = temperature
                self.humidity = humidity

                self.data.update({
                    'humidity': humidity,
                    'temperature': temperature
                })
        else:
            self.log.debug('unknown handle %X' % handle)
