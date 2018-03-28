
from ething.meta import method, iface

class Info (iface):
	
	@method.return_type('string')
	def getInformation(self):
		"""
		return the last information
		"""
		return self.get_value( 'V_TEXT' )
	
	
	
	