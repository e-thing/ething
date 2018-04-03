
from ething.meta import method
from ething.interfaces import RGBLight


class RGB_Light (RGBLight):
    
    
    def setColor(self, color):
        self.set_value( 'V_RGB', color )
    
    
    @method.meta(optional = 'V_WATT')
    @method.return_type('float')
    def getPower(self):
        """
        return the power of this light (in Watt)
        """
        return self.get_value( 'V_WATT' )
    
    