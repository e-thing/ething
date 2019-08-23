# coding: utf-8

from ething.Device import Device
from ething.reg import *
from ething.TransportProcess import TransportProcess, SerialTransport
from .protocol import RFLinkProtocol


CONTROLLER_NAME = 'rflink.controller'


class RFLinkController(TransportProcess):

    def __init__(self, gateway):
        super(RFLinkController, self).__init__(
            CONTROLLER_NAME,
            transport = SerialTransport(
                port = gateway.port,
                baudrate = gateway.baudrate
            ),
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
@attr('baudrate', type=Enum([110, 150, 300, 600, 1200, 2400, 4800, 9600, 19200, 38400, 57600, 115200]), default=57600, description="The baudrate")
@attr('port', type=SerialPort(), description="The serial port name.")
class RFLinkGateway(Device):
    """
    See http://www.rflink.nl
    """

    RESET_ATTR = ['port', 'baudrate']

    def __init__(self, *args, **kwargs):
        super(RFLinkGateway, self).__init__(*args, **kwargs)
        self.restart_controller()

    def on_update(self, dirty_keys):
        for attr in self.RESET_ATTR:
            if attr in dirty_keys:
                self.restart_controller()
                break

    @property
    def controller(self):
        return self.processes[CONTROLLER_NAME]

    def restart_controller(self):
        try:
            # kill any existing controller
            del self.processes[CONTROLLER_NAME]
        except KeyError:
            pass
        # create a new one
        self.processes.add(RFLinkController(self))

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
