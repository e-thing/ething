# coding: utf-8

from ..BleaDevice import BleaDevice
from ething.core.reg import *
from ething.core.interfaces import Thermometer, LightSensor, MoistureSensor

@attr('firmware', default='unknown', mode=READ_ONLY, description="The firmware version of this device.")
class Miflora(BleaDevice, Thermometer, LightSensor, MoistureSensor):
    
    name = 'miflora'
    readPeriod = 300
    
    @classmethod
    def isvalid(cls, name, manuf=''):
        validname = ['Flower mate','Flower care']
        if name in validname:
            return True
    
    def read(self):

        try:
            with self.connect() as conn:
                batteryFirm = bytearray(conn.readCharacteristic('0x38'))
                conn.writeCharacteristic('0x33','a01f',response=True)
                battery = batteryFirm[0]
                firmware = "".join([chr(c) for c in batteryFirm[2:]])
                
                with self:
                    self.firmware = firmware
                    self.battery = battery
                    self.setConnectState(True)
                    
                conn.writeCharacteristic('0x36','0100',response=True)

                conn.waitForNotifications(2)
                
                
        except Exception as e:
            self.log.error(str(e))
    
    
    def handleNotification(self,conn,handle,data):
        if hex(handle) == '0x35':
            received = bytearray(data)
            temperature = float(received[1] * 256 + received[0]) / 10
            sunlight = received[4] * 256 + received[3]
            moisture = received[7]
            fertility = received[9] * 256 + received[8]

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

