
from ething.meta import method, iface

class Dust (iface):
    
    @method.return_type('float')
    def getDust(self):
        """
        return the dust level.
        """
        return self.get_value( 'V_DISTANCE' )
    
    
    @method.meta(optional = 'V_UNIT_PREFIX')
    @method.return_type('float')
    def getUnit(self):
        """
        return the unit.
        """
        return self.get_value( 'V_UNIT_PREFIX' )
    