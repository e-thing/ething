# coding: utf-8
from future.utils import string_types, integer_types, iteritems
from ething.Device import Device, method, attr, isInteger, isBool


@attr('iface', validator=isInteger(min=0, max=9), default=0, description="The number of the bluetooth interface (hciX).")
@attr('learning', validator=isBool(), default=True, description="If true, new device will be automatically included.")
class BleaGateway(Device):
    """
    BLEA Gateway resource representation
    """
    pass
