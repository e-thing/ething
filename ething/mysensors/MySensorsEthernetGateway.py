# coding: utf-8


from .MySensorsGateway import MySensorsGateway
from ething.base import attr, isString


@attr('address', validator=isString(regex='^([-\\w.]+)(:[0-9]{1,5})?$'), description="The ip address or hostname of the gateway.")
class MySensorsEthernetGateway(MySensorsGateway):
    pass
