
from ething.meta import method, iface

class GPS (iface):
	
	
	@method.return_type('string')
	def getCoordinates(self):
		"""
		return the coordinates (format: latitude;longitude;altitude(m))
		"""
		return self.get_value( 'V_POSITION' )
	
	
	
	
	