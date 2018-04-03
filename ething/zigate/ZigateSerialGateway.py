

     
from ZigateGateway import ZigateGateway, attr, isString


@attr('port', validator = isString(), description="The serial port name.")
class ZigateSerialGateway (ZigateGateway):
    pass
    
    




