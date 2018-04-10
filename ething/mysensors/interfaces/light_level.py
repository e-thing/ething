# coding: utf-8

from ething.meta import method, iface

class Light_Level (iface):
    
    @method.meta(optional = 'V_LIGHT_LEVEL')
    @method.return_type('float')
    def getUncalibratedLightLevel(self):
        """
        return the uncalibrated light level. 0-100%.
        """
        return self.get_value( 'V_LIGHT_LEVEL' )
    
    
    @method.meta(optional = 'V_LEVEL')
    @method.return_type('float')
    def getLightLevel(self):
        """
        return the light level in lux.
        """
        return self.get_value( 'V_LEVEL' )
    
    