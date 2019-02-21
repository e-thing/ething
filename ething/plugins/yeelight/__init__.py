# coding: utf-8
from .YeelightBulbRGBW import YeelightBulbRGBW

from ething.core.plugin import Plugin
from ething.core.TransportProcess import TransportProcess, UdpTransport
from .protocol import YeelightAdvertisementProtocol
from .yeelight import MULTICAST_ADDRESS, MULTICAST_PORT


class Yeelight(Plugin):

    def setup(self):
        self.core.process_manager.add(AdvertisementController(self.core))


class AdvertisementController(TransportProcess):

    def __init__(self, core):
        super(AdvertisementController, self).__init__(
            'yeelight.adv',
            transport=UdpTransport(
                host=MULTICAST_ADDRESS,
                port=MULTICAST_PORT
            ),
            protocol=YeelightAdvertisementProtocol(core),
            reconnect_delay=60
        )

    def search(self, *args, **kwargs):
        self.protocol.search(*args, **kwargs)






