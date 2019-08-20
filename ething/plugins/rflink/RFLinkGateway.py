# coding: utf-8

from ething.core.Device import Device
from ething.core.reg import *
from ething.core.TransportProcess import TransportProcess
from .protocol import RFLinkProtocol


class RFLinkController(TransportProcess):
    RESET_ATTR = list()

    def __init__(self, gateway, transport):
        super(RFLinkController, self).__init__(
            'rflink.%s' % gateway.id,
            transport = transport,
            protocol = RFLinkProtocol(gateway)
        )
        self.gateway = gateway

    def on_open_state_changed(self):
        self.gateway.refresh_connect_state(self.is_open)

    def send(self, *args, **kwargs):
        return self.protocol.send(*args, **kwargs)


@abstract
@attr('version', default=None, mode=READ_ONLY, description="The version of the RFLink library used.")
@attr('revision', default=None, mode=READ_ONLY, description="The revision number of the RFLink library used.")
@attr('build', default=None, mode=READ_ONLY, description="The build number of the RFLink library used.")
@attr('inclusion', default=False, type=Boolean(),  description="If true, new devices will be automatically created.")
class RFLinkGateway(Device):
    """
    See http://www.rflink.nl
    """

    def __process__(self):
        self.controller = self.__controller__(self)
        return self.controller

    def on_update(self, dirty_keys):
        for attr in self.controller.RESET_ATTR:
            if attr in dirty_keys:
                self.controller.restart()
                break

    def getNodes(self, filter=None):
        def _filter (r):
            if r.createdBy == self and r.typeof('resources/RFLinkNode'):
                if filter:
                    return filter(r)
                return True
            return False

        return self.core.find(_filter)

    def getNode(self, filter):

        def _filter (r):
            if r.createdBy == self and r.typeof('resources/RFLinkNode'):
                if filter:
                    return filter(r)
                return True
            return False

        return self.core.find_one(_filter)

    @method.arg('message', type=String(allow_empty=False))
    def sendMessage(self, message):
        """
        send a message.
        """
        self.controller.send(message)

    def reboot(self):
        """
        reboot the gateway.
        """
        self.controller.send("10;REBOOT;")

    @method.return_type('text/plain')
    def getVersion(self):
        """
        get the version of the gateway.
        """
        result = self.controller.send("10;VERSION;", response = 'BUILD=') # VER=1.1;REV=46;BUILD=0c
        result.wait()

        if result.error:
            raise Exception(str(result.error))

        return result.data.split(';', 2)[-1]
