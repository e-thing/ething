# coding: utf-8

from ething.meta import method, iface

class Wind (iface):
    
    @method.return_type('float')
    def getWindSpeed(self):
        """
        return the wind speed (in km/h)
        """
        return self.get_value( 'V_WIND' )
    
    
    @method.meta(optional = 'V_GUST')
    @method.return_type('float')
    def getGustSpeed(self):
        """
        return the wind gusts speed (in km/h)
        """
        return self.get_value( 'V_GUST' )
    
    
    @method.meta(optional = 'V_DIRECTION')
    @method.return_type('float')
    def getDirection(self):
        """
        return the direction of the wind (degrees)
        """
        return self.get_value( 'V_DIRECTION' )
    