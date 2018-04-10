# coding: utf-8

from ething.meta import interface, method, iface


@interface
class Thermometer(iface):
    
    
    @method.return_type('float')
    def getTemperature(self):
        """
        return the current temperature (in degree Celsius)
        """
        return self.getData('temperature')
    
    




