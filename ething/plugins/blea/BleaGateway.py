# coding: utf-8
from ething.Device import Device
from ething.reg import *


@attr('learning', type=Boolean(), default=True, description="If true, new device will be automatically included.")
@attr('iface', type=BluetoothInterface(), default=0, description="The number of the bluetooth interface (hciX).", label="interface")
class BleaGateway(Device):
    """
    BLEA Gateway resource representation
    """
    pass
