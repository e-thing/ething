
from .ResourceEvent import ResourceEvent


class LowBatteryDevice(ResourceEvent):
	
	
	@staticmethod
	def validate (attributes, context):
		return ResourceEvent.validate(attributes, context, onlyTypes=['Device'])


