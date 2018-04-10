# coding: utf-8

from ething.meta import method, iface

class Color_Sensor (iface):
    
    @method.return_type('string')
    def getColor(self):
        """
        return the color (0xffffff format)
        """
        return "0x" + self.get_value( 'V_RGB' )
    
    