# coding: utf-8


from .ZigateGateway import ZigateGateway
from ething.reg import *


@attr('port', type=String(), description="The serial port name.")
class ZigateSerialGateway (ZigateGateway):
    pass
