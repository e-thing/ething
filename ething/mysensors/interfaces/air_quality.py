# coding: utf-8

from ething.meta import method, iface

class Air_Quality (iface):
    """
    see: https://www.mysensors.org/build/gas
    """
    
    @method.return_type('float')
    def getAirQuality(self):
        """
        return the air quality level
        """
        return self.get_value( 'V_LEVEL' )
    
    
    @method.meta(optional = 'V_UNIT_PREFIX')
    @method.return_type('float')
    def getUnit(self):
        """
        return the unit.
        """
        return self.get_value( 'V_UNIT_PREFIX' )
    
    
    