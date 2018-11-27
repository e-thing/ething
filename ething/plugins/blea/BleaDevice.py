# coding: utf-8
from future.utils import string_types, integer_types, iteritems
from ething.core.Device import Device
from ething.core.reg import *
from .connector import Connector


@abstract
@attr('mac', type=String(allow_empty=False, regex='^([0-9A-Fa-f]{2}:){5}([0-9A-Fa-f]{2})$'), description="The MAC address of the device.")
@attr('rssi', mode=READ_ONLY, default=None, description="The last received signal strength indicator of this device.")
class BleaDevice(Device):
    """
    BLEA Device resource representation
    """
    
    name = 'unknown'

    def __init__(self, data, create=True, context=None):
        self._peripheral = None
        self._iface_lock = None
        super(BleaDevice, self).__init__(data, create, context)

    def connect(self):
        return Connector(self.createdBy.iface, self.mac)
    
    @classmethod
    def handleDiscovery(cls, gateway, mac, data, name, rssi, connectable):
        
        ething = gateway.ething
        
        # does the device already exist !
        device = ething.findOne(lambda r: r.isTypeof('resources/BleaDevice') and r.mac == mac)
        
        if not device:
            if gateway.learning:
                device = ething.create(cls, {
                    'name': name or getattr(cls, 'name', None) or 'dev',
                    'mac': mac,
                    'createdBy': gateway.id
                })
                
                if device:
                    ething.log.info("BLEA: device created mac:%s name:%s , %s" % (mac, name, device))
                else:
                    ething.log.error("BLEA: unable to create the device mac:%s name:%s" % (mac, name))
            else:
                ething.log.warning("BLEA: skipping device creation (learning=false) mac:%s name:%s" % (mac, name))
        #else:
        #    ething.log.debug("BLEA: device already exists mac:%s name:%s , %s" % (mac, name, device))
        
        if device:
            with device:
                device.rssi = rssi
                device.setConnectState(True)
        
        return device
