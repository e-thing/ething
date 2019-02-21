# coding: utf-8

from .RFLinkGateway import RFLinkGateway, RFLinkController
from ething.core.reg import *
from ething.core.TransportProcess import SerialTransport


class RFLinkSerialController(RFLinkController):
    RESET_ATTR = ['port', 'baudrate']

    def __init__(self, gateway):
        super(RFLinkSerialController, self).__init__(gateway, SerialTransport(
            port = gateway.port,
            baudrate = gateway.baudrate
        ))


@attr('baudrate', type=Enum([110, 150, 300, 600, 1200, 2400, 4800, 9600, 19200, 38400, 57600, 115200]), default=57600, description="The baudrate")
@attr('port', type=SerialPort(), description="The serial port name.")
class RFLinkSerialGateway(RFLinkGateway):
    __controller__ = RFLinkSerialController
