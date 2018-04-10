# coding: utf-8

from ething.meta import method, iface

class Hum (iface):
    
    @method.return_type('float')
    def getHumidity(self):
        """
        return the humidity (in %)
        """
        return self.get_value( 'V_HUM' )
    
    
    