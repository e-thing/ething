# coding: utf-8

from .Action import Action
from ...Resource import ResourceType
from ...entity import *


@attr('args', type=Dict(allow_extra = True), default={}, description="The arguments passed to the method")
@attr('method', type=String(), description="The method name")
@attr('device', type=ResourceType(accepted_types=('resources/Device',)), description="The device on which the action is executed")
class ExecuteDevice(Action):
    def run(self, signal, core):
        device = core.get(self.device)

        if device is None:
            raise Exception("the device has been removed")

        device.interface.call(self.method, **self.args)
