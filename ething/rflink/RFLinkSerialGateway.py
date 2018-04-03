



from RFLinkGateway import RFLinkGateway
from ething.base import attr, isString, isInteger, isEnum

@attr('baudrate', validator = isInteger() & isEnum([110,150,300,600,1200,2400,4800,9600,19200,38400,57600,115200]), default = 57600, description="The baudrate")
@attr('port', validator = isString(), description="The serial port name.")
class RFLinkSerialGateway(RFLinkGateway):
    pass
    
    

if __name__ == "__main__":
    
    from ething.core import Core
    from random import randint
    import time
    
    core = Core({
        'db':{
            'database': 'test'
        },
        'log':{
            'level': 'debug'
        }
    })
    
    device = None
    
    devices = core.find({
        'type': 'RFLinkSerialGateway'
    })
    
    if len(devices) > 1:
    
        for d in devices:
            print 'remove previous device...', d
            d.remove()
    
    elif len(devices) == 1:
        device = devices[0]
    
    if not device:
        device = core.create('RFLinkSerialGateway', {
            'name': 'rflink_gateway',
            'port': '/dev/ttyUSB0'
        })
    
    
    print device
    
    print device.data
    
    print device.getVersion()
    
