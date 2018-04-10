# coding: utf-8



from .MihomeDevice import MihomeDevice
from ething.interfaces import Thermometer

class MihomeSensorHT(MihomeDevice, Thermometer):
    """
    Mihome temperature/humidity/pressure Sensor Device class.
    """
    
    def processAttr(self, name, value):
        
        if name == 'temperature':
            value = int(value)/100.0
        
        if name == 'humidity':
            value = int(value)/100.0
        
        if name == 'pressure': # hPa
            value = int(value)
        
        self.store(name, value)
    
    
    
    




 