# coding: utf-8
from .YeelightBulbRGBW import YeelightBulbRGBW
from .YeelightBulbMono import YeelightBulbMono

from ething.plugin import Plugin
from ething.TransportProcess import TransportProcess, UdpTransport
from .protocol import YeelightAdvertisementProtocol
from .yeelight import MULTICAST_ADDRESS, MULTICAST_PORT
import logging

LOGGER = logging.getLogger(__name__)


class Yeelight(Plugin):

    def setup(self):
        self.processes.add(AdvertisementController(self.core))


class AdvertisementController(TransportProcess):

    def __init__(self, core):
        super(AdvertisementController, self).__init__(
            transport=UdpTransport(
                host=MULTICAST_ADDRESS,
                port=MULTICAST_PORT
            ),
            protocol=YeelightAdvertisementProtocol(core),
            reconnect_delay=60,
            logger=LOGGER
        )

    def search(self, *args, **kwargs):
        self.protocol.search(*args, **kwargs)






