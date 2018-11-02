# coding: utf-8

from ething.core.Device import Device
from ething.core.reg import *
from ething.core.interfaces import Light
from ething.core.Process import get_process


@abstract
@attr('fw_ver', type=String(), mode=READ_ONLY, description="The firmware version of the device.")
@attr('model', type=String(), mode=READ_ONLY, description="The model of the device.")
@attr('dev_id', mode = PRIVATE)
@attr('host', type=String(allow_empty=False), mode=READ_ONLY, description="The ip address of the device.")
class YeelightDevice (Device, Light):

    def _update(self, params):
        if "power" in params:
            state = bool('on' in params["power"].lower())
            self.state = state

    @property
    def controller(self):
        return get_process('yeelight.%s' % self.id)

    def setState(self, state):
        result = self.controller.send("set_power", ['on' if state else 'off', "smooth", 500], done = lambda _, device : setattr(device, 'state', state) )

        result.wait()

        if result.error:
            raise Exception(str(result.error))




