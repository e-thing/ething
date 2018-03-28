

from ething.meta import interface, method, iface


@interface
class Dimmable(iface):
	
	
	@method.return_type('float')
	def getLevel(self):
		"""
		return the current level of this dimmable switch
		"""
		return self.getData('level', 0)
	
	
	@method.arg('level', type='float', minimum=0, maximum=100)
	def setLevel(self, level):
		"""
		set the current level of this dimmable switch
		"""
		raise NotImplementedError()
	

