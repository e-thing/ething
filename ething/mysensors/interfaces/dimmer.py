
from ething.meta import method
from ething.interfaces import DimmableSwitch
from .. import MySensors

class Dimmer (DimmableSwitch):
	
	
	
	def getLevel(self):
		return self.get_value('V_PERCENTAGE')
	
	def setLevel(self, level):
		self.set_value( 'V_PERCENTAGE', level )
	
	def getState(self):
		
		statusAttrName = MySensors.valueTypeToName('V_STATUS')
		
		if self.hasData(statusAttrName):
			return self.get_value('V_STATUS')
		else:
			# determine the state from the percentage only value (on if percentage > 0 else off)
			return self.getLevel() > 0
	
	def setState(self, state):
		
		statusAttrName = MySensors.valueTypeToName('V_STATUS')
		
		if self.hasData(statusAttrName):
			self.set_value( 'V_STATUS', state )
		else:
			self.set_value( 'V_PERCENTAGE', 100 if state else 0 )
	
	
	@method.meta(optional = 'V_WATT')
	@method.return_type('float')
	def getPower(self):
		"""
		return the power of this switch (in Watt)
		"""
		return self.get_value( 'V_WATT' )
	
	