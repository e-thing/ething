# coding: utf-8
from future.utils import string_types, integer_types, iteritems
from ething.Device import Device, method, attr, isString, abstract
from .connector import Connector

@abstract
@attr('mac', validator=isString(allow_empty=False, regex='^([0-9A-Fa-f]{2}:){5}([0-9A-Fa-f]{2})$'), description="The MAC address of the device.")
class BleaDevice(Device):
    """
    BLEA Device resource representation
    """
    
    name = 'unknown'
    readPeriod = 60
    
    def connect(self):
        return Connector(self)
    
    @classmethod
    def handleDiscovery(cls, gateway, mac, data, name, rssi, connectable):
        
        ething = gateway.ething
        
        # does the device already exist !
        device = ething.findOne({
            'extends': 'BleaDevice',
            'mac': mac
        })
        
        if not device:
            if gateway.learning:
                device = ething.create(cls.__name__, {
                    'name': name or cls.name or 'dev',
                    'mac': mac,
                    'createdBy': gateway
                })
                
                if device:
                    ething.log.info("BLEA: device created mac:%s name:%s , %s" % (mac, name, device))
                else:
                    ething.log.error("BLEA: unable to create the device mac:%s name:%s" % (mac, name))
            else:
                ething.log.warning("BLEA: skipping device creation (learning=false) mac:%s name:%s" % (mac, name))
        #else:
        #    ething.log.debug("BLEA: device already exists mac:%s name:%s , %s" % (mac, name, device))
        
        return device