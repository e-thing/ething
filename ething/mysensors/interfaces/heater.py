# coding: utf-8

from ething.meta import method, iface
from .temp import Temp
from .binary import Binary

class Heater (Temp, Binary):
    
    
    @method.return_type('float')
    def getHeatTemperatureSetPoint(self):
        """
        return the heat temperature set point.
        """
        return self.get_value( 'V_HVAC_SETPOINT_HEAT' )
    
    @method.arg('temperature', type='float')
    def setHeatTemperatureSetPoint(self, temperature):
        """
        set the heat temperature set point.
        """
        self.set_value( 'V_HVAC_SETPOINT_HEAT' , temperature)
    
    @method.return_type('string')
    def getFlowState(self):
        """
        return the flow state.
        """
        return self.get_value( 'V_HVAC_FLOW_STATE' )
    
    @method.arg('state', type='string', enum=["Off", "HeatOn", "CoolOn", "AutoChangeOver"])
    def setFlowState(self, state):
        """
        set the flow state.
        """
        self.set_value( 'V_HVAC_FLOW_STATE', state )
    
    
    