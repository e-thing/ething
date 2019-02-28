# coding: utf-8

from ething.core.Device import Device
from ething.core.reg import *
from ething.core.interfaces import Light
from ething.core.TransportProcess import TransportProcess, NetTransport, UdpTransport, Protocol
from .protocol import YeelightProtocol
from .yeelight import PORT


class Controller(TransportProcess):

    def __init__(self, device):
        super(Controller, self).__init__(
            'yeelight.%s' % device.id,
            transport=NetTransport(
                host=device.host,
                port=PORT
            ),
            protocol=YeelightProtocol(device)
        )
        self.device = device

    def send(self, *args, **kwargs):
        return self.protocol.send(*args, **kwargs)


@abstract
@attr('fw_ver', type=String(), mode=READ_ONLY, description="The firmware version of the device.")
@attr('model', type=String(), mode=READ_ONLY, description="The model of the device.")
@attr('dev_id', mode = PRIVATE)
@attr('host', type=String(allow_empty=False), mode=READ_ONLY, description="The ip address of the device.")
class YeelightDevice (Light):

    def __process__(self):
        self.controller = Controller(self)
        return self.controller

    def on_update(self, dirty_keys):
        if 'host' in dirty_keys:
            self.controller.restart()

    def _update(self, params):
        if "power" in params:
            state = bool('on' in params["power"].lower())
            self.state = state

    def setState(self, state):
        result = self.controller.send("set_power", ['on' if state else 'off', "smooth", 500], done = lambda _, device : setattr(device, 'state', state) )

        result.wait()

        if result.error:
            raise Exception(str(result.error))




