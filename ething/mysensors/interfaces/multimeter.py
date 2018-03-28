
from ething.meta import method, iface

class Multimeter (iface):
	
	@method.meta(optional = 'V_VOLTAGE')
	@method.return_type('float')
	def getVoltage(self):
		"""
		return the voltage
		"""
		return self.get_value( 'V_VOLTAGE' )
	
	@method.meta(optional = 'V_CURRENT')
	@method.return_type('float')
	def getCurrent(self):
		"""
		return the current
		"""
		return self.get_value( 'V_CURRENT' )
	
	@method.meta(optional = 'V_IMPEDANCE')
	@method.return_type('float')
	def getImpedance(self):
		"""
		return the impedance
		"""
		return self.get_value( 'V_IMPEDANCE' )
	