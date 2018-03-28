
from .ResourceEvent import ResourceEvent


class DeviceDisconnected(ResourceEvent):
	
	
	@staticmethod
	def validate (attributes, context):
		return ResourceEvent.validate(attributes, context, onlyTypes=['Device'])