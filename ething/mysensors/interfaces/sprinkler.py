
from ething.meta import method
from ething.interfaces import Switch


class Sprinkler (Switch):
	
	def setState(self, state):
		self.set_value( 'V_STATUS', state )
	
	
	@method.meta(optional = 'V_TRIPPED')
	@method.return_type('bool')
	def isTripped(self):
		"""
		return true if the device is tripped
		"""
		return self.get_value( 'V_TRIPPED' )
	
	