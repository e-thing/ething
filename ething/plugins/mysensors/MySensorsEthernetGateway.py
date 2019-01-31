# coding: utf-8


from .MySensorsGateway import MySensorsGateway
from ething.core.reg import *


@attr('port', type=Integer(min=0, max=65535), default=5003, description="The port number of the gateway. The default port number is 5003.")
@attr('host', type=Host(), description="The ip address or hostname of the gateway.")
class MySensorsEthernetGateway(MySensorsGateway):
    pass
