# coding: utf-8
from ething.Device import Device
from ething.reg import *


@attr('iface', type=Integer(min=0, max=9), default=0, description="The number of the bluetooth interface (hciX).")
@attr('learning', type=Boolean(), default=True, description="If true, new device will be automatically included.")
class BleaGateway(Device):
    """
    BLEA Gateway resource representation
    """
    pass
