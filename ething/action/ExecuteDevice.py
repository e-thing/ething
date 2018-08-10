# coding: utf-8

from .Action import Action
from ething.Resource import ResourceType
from ething.reg import *


@attr('args', type=Dict(allow_extra = True), default={}, description="The arguments passed to the method")
@attr('method', type=String(), description="The method name")
@attr('device', type=ResourceType(accepted_types=('resources/Device',)), description="The device on which the action is executed")
class ExecuteDevice(Action):

    def run(self, signal):
        device = self.device

        if device is None:
            raise Exception("the device has been removed")

        device.interface.call(self.method, **self.args)


    def __getattr__(self, name):
        value = super(ExecuteDevice, self).__getattr__(name)

        if name == 'device':
            return self.ething.get(value)
        else:
            return value
