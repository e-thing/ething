# coding: utf-8


from .MySensorsGateway import MySensorsGateway
from ething.reg import *


@attr('host', validator=String(allow_empty=False), description="The ip address or hostname of the gateway.")
@attr('port', validator=Integer(min=0, max=65535), default=5003, description="The port number of the gateway. The default port number is 5003.")
class MySensorsEthernetGateway(MySensorsGateway):
    pass
