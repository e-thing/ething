
from .ResourceEvent import ResourceEvent


class FileDataModified(ResourceEvent):
	
	
	@staticmethod
	def validate (attributes, context):
		return ResourceEvent.validate(attributes, context, onlyTypes=['File'])