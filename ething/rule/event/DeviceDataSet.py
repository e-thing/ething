

from .ResourceEvent import ResourceEvent

class DeviceDataSet(ResourceEvent):
	
	@classmethod
	def emit (cls, device, data):
		return super(DeviceDataSet, cls).emit(device, {
			'data' : data
		})
	
	@staticmethod
	def validate (attributes, context):
		return ResourceEvent.validate(attributes, context, onlyTypes=['Device'])
	
	
	
	

