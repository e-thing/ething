
from ething.meta import method, interface
from ething.interfaces import RGBWLight


class RGBW_Light (RGBWLight):
    
    
    def setLevel(self, level):
        self.set_value( 'V_RGBW', (self.getColor(), level))
    
    def setColor(self, color):
        self.set_value( 'V_RGBW', (color, self.getLevel()))
    
    
    @method.meta(optional = 'V_WATT')
    @method.return_type('float')
    def getPower(self):
        """
        return the power of this light (in Watt)
        """
        return self.get_value( 'V_WATT' )
    
    