
from ething.meta import method, iface

class Weight (iface):
	
	@method.return_type('float')
	def getWeight(self):
		"""
		return the weight (in Kg)
		"""
		return self.get_value( 'V_WEIGHT' )
	
	
	@method.meta(optional = 'V_IMPEDANCE')
	@method.return_type('float')
	def getImpedance(self):
		"""
		return the impedance of the weight
		"""
		return self.get_value( 'V_IMPEDANCE' )
	
	