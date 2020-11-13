# coding: utf-8
from .RFLinkSwitch import RFLinkSwitch
from .RFLinkGenericSensor import RFLinkGenericSensor


from ething.reg import *
from ething.plugin import Plugin
from ething.TransportProcess import TransportProcess, SerialTransport
from .protocol import RFLinkProtocol


class RFLinkController(TransportProcess):

    def __init__(self, plugin, id=None):

        port = plugin.options.get('port')
        baudrate = int(plugin.options.get('baudrate', 57600))

        super(RFLinkController, self).__init__(
            id=id,
            transport = SerialTransport(
                port = port,
                baudrate = baudrate
            ),
            protocol = RFLinkProtocol(plugin),
            logger=plugin.logger
        )

        self.plugin = plugin

    def on_open_state_changed(self):
        self.plugin.connected = self.is_open

    def send(self, *args, **kwargs):
        return self.protocol.send(*args, **kwargs)


@attr('version', default=None, mode=READ_ONLY, description="The version of the RFLink library used.")
@attr('revision', default=None, mode=READ_ONLY, description="The revision number of the RFLink library used.")
@attr('build', default=None, mode=READ_ONLY, description="The build number of the RFLink library used.")
@attr('inclusion', default=False, type=Boolean(),  description="If true, new devices will be automatically created.")
@attr('connected', type=Boolean(), default=False, mode=READ_ONLY, description="Set to true when connected to the RFLink gateway.")
class RFLink(Plugin):

    def setup(self):
        self.controller = None

        if not self.options.get('port'):
            self.logger.warning("no port set in the configuration file")
            self.connected = False
            self.notification.warning('no port set in the configuration file', title='RFLink',
                                           id='rflink.check')
            return

        self.notification.remove('rflink.check')
        self.controller = RFLinkController(self, 'rflink.controller')
        self.processes.add(self.controller)

    def getNodes(self, filter=None):
        def _filter (r):
            if r.typeof('resources/RFLinkNode'):
                if filter:
                    return filter(r)
                return True
            return False

        return self.core.find(_filter)

    def getNode(self, filter):

        def _filter (r):
            if r.typeof('resources/RFLinkNode'):
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

    @method
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