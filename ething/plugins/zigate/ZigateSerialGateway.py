# coding: utf-8


from .ZigateGateway import ZigateGateway
from ething.core.reg import *


@attr('port', type=SerialPort(), description="The serial port name.")
class ZigateSerialGateway (ZigateGateway):
    pass
