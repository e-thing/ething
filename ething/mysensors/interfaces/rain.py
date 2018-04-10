# coding: utf-8

from ething.meta import method, iface

class Rain (iface):
    """
    see: https://www.mysensors.org/build/rain
    """
    
    @method.return_type('float')
    def getRain(self):
        """
        return the rainfall (in mm)
        """
        return self.get_value( 'V_RAIN' )
    
    
    @method.meta(optional = 'V_RAINRATE')
    @method.return_type('float')
    def getRainRate(self):
        """
        return the rain rate (in mm/h)
        """
        return self.get_value( 'V_RAINRATE' )
    
    
    