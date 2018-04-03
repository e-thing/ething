



from ZigateDevice import ZigateDevice
import Zigate


@Zigate.model('lumi.weather', 'thermometer himidity pressure sensor')
class ZigateAqaraTHP(ZigateDevice):
    """
    Mihome temperatire/humidity/pressure Sensor Device class.
    """
    
    def onMessage (self, message):
        pass # todo
        
        
    





 