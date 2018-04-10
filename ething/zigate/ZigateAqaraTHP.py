# coding: utf-8




from .ZigateDevice import ZigateDevice
from .helpers import model


@model('lumi.weather', 'thermometer himidity pressure sensor')
class ZigateAqaraTHP(ZigateDevice):
    """
    Mihome temperatire/humidity/pressure Sensor Device class.
    """
    
    def onMessage (self, message):
        pass # todo
        
        
    





 