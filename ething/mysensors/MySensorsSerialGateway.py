# coding: utf-8


from .MySensorsGateway import MySensorsGateway
from ething.base import attr, isString, isInteger, isEnum


@attr('baudrate', validator=isInteger() & isEnum([110, 150, 300, 600, 1200, 2400, 4800, 9600, 19200, 38400, 57600, 115200]), default=57600, description="The baudrate.")
@attr('port', validator=isString(), description="The serial port name.")
class MySensorsSerialGateway(MySensorsGateway):
    pass
