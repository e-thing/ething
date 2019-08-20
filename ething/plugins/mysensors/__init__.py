# coding: utf-8
from .MySensorsGateway import MySensorsGateway
from .MySensorsSerialGateway import MySensorsSerialGateway
from .MySensorsEthernetGateway import MySensorsEthernetGateway
# from .MySensorsFakeGateway import MySensorsFakeGateway
from .MySensorsNode import MySensorsNode
from .MySensorsSensor import MySensorsSensor
from .helpers import check_mysgw, DEFAULT_ETH_PORT
from ething.core import Plugin


class MySensorsPlugin (Plugin):

    def setup(self):
        self.core.scheduler.delay(0, self.check_mysgw)

    def check_mysgw(self):
        if not self.core.find_one(lambda r: r.typeof('resources/MySensorsGateway')):
            self.log.debug("try to find any running local instance of mysgw")
            version = check_mysgw()
            if version is not None:
                self.log.info("local instance of mysgw found: version=%s", version)
                self.core.create(MySensorsEthernetGateway, {
                    'name': 'mysgw',
                    'host': 'localhost',
                    'port': DEFAULT_ETH_PORT
                })
            else:
                self.log.debug("no running local instance of mysgw found")
