# coding: utf-8
from .MihomeGateway import MihomeGateway
from .MihomeSensorHT import MihomeSensorHT
from .MihomeMagnet import MihomeMagnet
from .MihomeButton import MihomeButton
from ething.core.plugin import Plugin
from ething.core.TransportProcess import TransportProcess, UdpTransport, ThreadedTransport
from .helpers import *
from .protocol import MihomeProtocol


class Mihome(Plugin):

    def setup(self):
        self.controller = self.core.process_manager.attach(Controller(self.core))


class Controller(TransportProcess):

    def __init__(self, core):
        super(Controller, self).__init__(
            'mihome',
            transport=UdpTransport(
                host=MULTICAST_ADDRESS,
                port=MULTICAST_PORT
            ),
            #transport=ThreadedTransport(UdpTransport(
            #    host=MULTICAST_ADDRESS,
            #    port=MULTICAST_PORT
            #), core.process_manager, 'mihome.read'),

            protocol=MihomeProtocol(core),
            id='mihome'
        )
        self.core = core

    def on_open_state_changed(self):
        for gateway in self.core.find(lambda r: r.isTypeof(MihomeGateway)):
            gateway.refresh_connect_state(self.is_open)

    def send(self, *args, **kwargs):
        return self.protocol.send(*args, **kwargs)



