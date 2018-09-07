# coding: utf-8


from .MySensorsGateway import MySensorsGateway
from ething.core.reg import *


@attr('baudrate', type=Enum([110, 150, 300, 600, 1200, 2400, 4800, 9600, 19200, 38400, 57600, 115200]), default=57600, description="The baudrate.")
@attr('port', type=String(allow_empty=False), description="The serial port name.")
class MySensorsSerialGateway(MySensorsGateway):
    pass
