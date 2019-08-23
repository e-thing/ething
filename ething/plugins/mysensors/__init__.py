# coding: utf-8
from .MySensorsGateway import MySensorsGateway
from .MySensorsSerialGateway import MySensorsSerialGateway
from .MySensorsEthernetGateway import MySensorsEthernetGateway
# from .MySensorsFakeGateway import MySensorsFakeGateway
from .MySensorsNode import MySensorsNode
from .MySensorsSensor import MySensorsSensor
from .helpers import check_mysgw, DEFAULT_ETH_PORT
from ething import Plugin
from ething.scheduler import delay
import logging


LOGGER = logging.getLogger(__name__)


class MySensorsPlugin (Plugin):

    def setup(self):
        self.core.processes.add(self.check_mysgw) # make it async !

    def check_mysgw(self):
        if not self.core.find_one(lambda r: r.typeof('resources/MySensorsGateway')):
            LOGGER.debug("try to find any running local instance of mysgw")
            version = check_mysgw()
            if version is not None:
                LOGGER.info("local instance of mysgw found: version=%s", version)
                self.core.create(MySensorsEthernetGateway, {
                    'name': 'mysgw',
                    'host': 'localhost',
                    'port': DEFAULT_ETH_PORT
                })
            else:
                LOGGER.debug("no running local instance of mysgw found")
