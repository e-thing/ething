
from .ResourceEvent import ResourceEvent


class DeviceConnected(ResourceEvent):
    
    
    @staticmethod
    def validate (attributes, context):
        return ResourceEvent.validate(attributes, onlyTypes=['Device'])