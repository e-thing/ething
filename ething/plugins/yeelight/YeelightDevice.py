# coding: utf-8

from ething.Device import Device
from ething.reg import *
from ething.interfaces import Light
from ething.TransportProcess import TransportProcess, NetTransport, UdpTransport, Protocol
from .protocol import YeelightProtocol
from .yeelight import PORT


class Controller(TransportProcess):

    def __init__(self, device):
        super(Controller, self).__init__(
            transport=NetTransport(
                host=device.host,
                port=PORT
            ),
            protocol=YeelightProtocol(device),
            logger=device.logger
        )
        self.device = device

    def on_open_state_changed(self):
        self.device.refresh_connect_state(self.is_open)

    def send(self, *args, **kwargs):
        return self.protocol.send(*args, **kwargs)


@abstract
@meta(disable_creation=True)
@attr('_support', default=[], mode=PRIVATE)
@attr('fw_ver', type=String(), mode=READ_ONLY, description="The firmware version of the device.")
@attr('model', type=String(), mode=READ_ONLY, description="The model of the device.")
@attr('dev_id', mode = PRIVATE)
@attr('host', type=Host(), mode=READ_ONLY, description="The ip address of the device.")
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




