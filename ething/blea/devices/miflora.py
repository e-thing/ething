# coding: utf-8

from ..BleaDevice import BleaDevice
from ething.base import attr, READ_ONLY
from ething.interfaces import Thermometer

@attr('firmware', default='unknown', mode=READ_ONLY, description="The firmware version of this device.")
class Miflora(BleaDevice, Thermometer):
    
    name = 'miflora'
    readPeriod = 300
    
    @classmethod
    def isvalid(cls, name, manuf=''):
        validname = ['Flower mate','Flower care']
        if name in validname:
            return True
    
    def read(self):
        
        result={}
        try:
            with self.connect() as conn:
                batteryFirm = bytearray(conn.readCharacteristic('0x38'))
                conn.writeCharacteristic('0x33','a01f',response=True)
                battery = batteryFirm[0]
                firmware = "".join(map(chr, batteryFirm[2:]))
                
                with self:
                    self._firmware = firmware
                    self.battery = battery
                    self.setConnectState(True)
                    
                    conn.writeCharacteristic('0x36','0100',response=True)
                    
                    conn.waitForNotifications(2)
                
                
        except Exception as e:
            self.ething.log.error(str(e))
        
        return result
    
    
    def handleNotification(self,conn,handle,data):
        if hex(handle) == '0x35':
            received = bytearray(data)
            temperature = float(received[1] * 256 + received[0]) / 10
            sunlight = received[4] * 256 + received[3]
            moisture = received[7]
            fertility = received[9] * 256 + received[8]
            
            data = {
                'sunlight': sunlight,
                'moisture': moisture,
                'fertility': fertility,
                'temperature': temperature
            }
            
            # self.ething.log.debug(str(data))
            
            self.store('data', data)

