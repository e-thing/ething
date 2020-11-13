# coding: utf-8
from .MihomeGateway import MihomeGateway
from .MihomeSensorHT import MihomeSensorHT
from .MihomeMagnet import MihomeMagnet
from .MihomeButton import MihomeButton
from ething.plugin import Plugin
from ething.TransportProcess import TransportProcess, UdpTransport
from .helpers import *
from .protocol import MihomeProtocol
import logging

LOGGER = logging.getLogger(__name__)

class Mihome(Plugin):

    def setup(self):
        self.controller = self.core.processes.add(Controller(self.core))


class Controller(TransportProcess):

    def __init__(self, core):
        super(Controller, self).__init__(
            id='mihome',
            transport=UdpTransport(
                host=MULTICAST_ADDRESS,
                port=MULTICAST_PORT
            ),
            protocol=MihomeProtocol(core),
            logger=LOGGER
        )
        self.core = core

    def on_open_state_changed(self):
        for gateway in self.core.find(lambda r: r.typeof(MihomeGateway)):
            gateway.refresh_connect_state(self.is_open)

    def send(self, *args, **kwargs):
        return self.protocol.send(*args, **kwargs)



