# coding: utf-8

from ething.meta import method, iface

class Baro (iface):
    
    @method.return_type('float')
    def getPressure(self):
        """
        return the pressure (in Pa)
        """
        return self.get_value( 'V_PRESSURE' )
    
    
    @method.meta(optional = 'V_FORECAST')
    @method.return_type('string')
    def getForecast(self):
        """
        return the forecast
        """
        return self.get_value( 'V_FORECAST' )
    