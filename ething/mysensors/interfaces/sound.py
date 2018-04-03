
from ething.meta import method, iface

class Sound (iface):
    
    @method.meta(optional = 'V_LEVEL')
    @method.return_type('float')
    def getLevel(self):
        """
        return the sound level.
        """
        return self.get_value( 'V_LEVEL' )
    
    
    @method.meta(optional = 'V_TRIPPED')
    @method.return_type('bool')
    def isTripped(self):
        """
        return true if the device is tripped.
        """
        return self.get_value( 'V_TRIPPED' )
    
    
    
    @method.meta(optional = 'V_ARMED')
    @method.return_type('bool')
    def isArmed(self):
        """
        return true if the device is armed.
        """
        return self.get_value( 'V_ARMED' )
    
    