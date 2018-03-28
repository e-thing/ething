
from light import Light
from ething.meta import method, interface


def toHex(value):
	return value



@interface
class RGBLight (Light):
	
	
	@method.return_type('string')
	def getColor(self):
		"""
		return the color of the light (#ffffff format)
		"""
		return toHex(self.getData('color', '#FFFFFF'))
	
	
	@method.arg('color', type='string', format='color')
	def setColor(self, color):
		"""
		set the color of the light (#ffffff format)
		"""
		raise NotImplementedError()
	
	

	