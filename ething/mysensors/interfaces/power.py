
from ething.meta import method, iface

class Power (iface):
	
	
	@method.meta(optional = 'V_WATT')
	@method.return_type('float')
	def getPower(self):
		"""
		return the power (in Watt)
		"""
		return self.get_value( 'V_WATT' )
	
	
	@method.meta(optional = 'V_KWH')
	@method.return_type('float')
	def getEnergy(self):
		"""
		return the energy (in KWH)
		"""
		return self.get_value( 'V_KWH' )
	
	
	@method.meta(optional = 'V_VAR')
	@method.return_type('float')
	def getReactivePower(self):
		"""
		return the reactive power: volt-ampere reactive
		"""
		return self.get_value( 'V_VAR' )
	
	
	@method.meta(optional = 'V_VA')
	@method.return_type('float')
	def getApparentPower(self):
		"""
		return the apparent power: volt-ampere (VA)
		"""
		return self.get_value( 'V_VA' )
	
	
	@method.meta(optional = 'V_POWER_FACTOR')
	@method.return_type('float')
	def getPowerFactor(self):
		"""
		return the ratio of real power to apparent power: floating point value in the range [-1,..,1]
		"""
		return self.get_value( 'V_POWER_FACTOR' )
	