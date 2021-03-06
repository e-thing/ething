# coding: utf-8


from .MySensorsGateway import MySensorsGateway, MySensorsController
from .helpers import DEFAULT_ETH_PORT
from ething.core.reg import *
from ething.core.TransportProcess import NetTransport


class MySensorsEthernetController(MySensorsController):
    RESET_ATTR = ['port', 'host']

    def __init__(self, gateway):
        super(MySensorsEthernetController, self).__init__(gateway, NetTransport(
            host=gateway.host,
            port=gateway.port
        ))


@attr('port', type=Integer(min=0, max=65535), default=DEFAULT_ETH_PORT, description="The port number of the gateway. The default port number is %d." % DEFAULT_ETH_PORT)
@attr('host', type=Host(), description="The ip address or hostname of the gateway.")
class MySensorsEthernetGateway(MySensorsGateway):
    __controller__ = MySensorsEthernetController
