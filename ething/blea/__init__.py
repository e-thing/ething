# coding: utf-8
from future.utils import string_types

from .Controller import Controller
from .BleaGateway import BleaGateway, Device


class blea(object):

    def __init__(self, core):
        self.core = core
        self.log = core.log
        self.rpc = core.rpc

        self.controllers = {}

        self.core.signalManager.bind(
            'ResourceCreated', self.on_resource_created)
        self.core.signalManager.bind(
            'ResourceDeleted', self.on_resource_deleted)

        devices = self.core.find({
            'type': 'BleaGateway'
        })

        for device in devices:
            try:
                self.start_controller(device)
            except Exception as e:
                self.log.error(e)

    def on_resource_created(self, signal):
        device = self.core.get(signal['resource'])
        if isinstance(device, BleaGateway):
            self.start_controller(device)

    def on_resource_deleted(self, signal):
        device = self.core.get(signal['resource'])
        if isinstance(device, BleaGateway):
            self.stop_controller(device)

    def start_controller(self, device):

        if isinstance(device, string_types):
            device = self.core.get(device)

        if not device or not isinstance(device, BleaGateway):
            raise Exception(
                "the device %s does not exist or has the wrong type" % str(device))

        # remove any previous stream from this device
        self.stop_controller(device)

        self.log.info("starting BleaGateway controller '%s' id=%s type=%s" %
                      (device.name, device.id, device.type))

        controller = Controller(device)

        self.controllers[device.id] = controller

        return controller

    def stop_controller(self, device):

        if isinstance(device, Device):
            device = device.id

        if device in self.controllers:
            controller = self.controllers[device]
            self.log.info("stopping BleaGateway controller '%s' id=%s type=%s" % (
                controller.gateway.name, controller.gateway.id, controller.gateway.type))
            controller.destroy()
            del self.controllers[device]

    def stop_all_controllers(self):
        for id in list(self.controllers):
            self.stop_controller(id)
        self.controllers = {}

