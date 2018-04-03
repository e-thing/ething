
from ething.meta import method, iface
from heater import Heater

class HVAC (Heater):
    
    @method.return_type('float')
    def getCoolTemperatureSetPoint(self):
        """
        return the cool temperature set point.
        """
        return self.get_value( 'V_HVAC_SETPOINT_COOL' )
    
    @method.arg('temperature', type='float')
    def setCoolTemperatureSetPoint(self, temperature):
        """
        set the cool temperature set point.
        """
        self.set_value( 'V_HVAC_SETPOINT_COOL' , temperature)
    
    @method.return_type('string')
    def getFlowMode(self):
        """
        return the flow mode.
        """
        return self.get_value( 'V_HVAC_FLOW_MODE' )
    
    @method.arg('mode', type='string', enum=["Auto", "ContinuousOn", "PeriodicOn"])
    def setFlowMode(self, mode):
        """
        set the flow mode.
        """
        self.set_value( 'V_HVAC_FLOW_MODE', mode )
    
    @method.return_type('string')
    def getSpeed(self):
        """
        return the speed.
        """
        return self.get_value( 'V_HVAC_SPEED' )
    
    @method.arg('speed', type='string', enum=["Auto", "ContinuousOn", "PeriodicOn"])
    def setSpeed(self, speed):
        """
        set the speed.
        """
        self.set_value( 'V_HVAC_SPEED', speed )
    
    
    