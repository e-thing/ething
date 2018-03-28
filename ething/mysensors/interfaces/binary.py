
from ething.meta import method
from ething.interfaces import Switch


class Binary (Switch):
	
	
	def setState(self, state):
		self.set_value( 'V_STATUS', state )
	
	
	@method.meta(optional = 'V_WATT')
	@method.return_type('float')
	def getPower(self):
		"""
		return the power of this switch (in Watt)
		"""
		return self.get_value( 'V_WATT' )
	
	