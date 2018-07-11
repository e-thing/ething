# coding: utf-8

from .Action import Action
from ething.Resource import isResource, ResourceModelAdapter
from ething.base import attr, isString, isObject


@attr('args', validator=isObject(allow_extra = True), default={}, description="The arguments passed to the method")
@attr('method', validator=isString(), description="The method name")
@attr('device', validator=isResource(accepted_types=('Device',)), model_adapter=ResourceModelAdapter(), description="The device on which the action is executed")
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
