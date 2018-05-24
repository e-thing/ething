# coding: utf-8

from .Controller import Controller
from .MihomeGateway import MihomeGateway, Device
from .MihomeSensorHT import MihomeSensorHT


class Mihome(object):

    def __init__(self, core):
        self.core = core
        self.log = core.log
        self.rpc = core.rpc

        self.controller = None

        self.rpc.register('device.mihome.send',
                          self.controller_send, callback_name='callback')

        self.start_controller()

    def start_controller(self):

        # remove any previous stream from this device
        self.stop_controller()

        self.log.info("starting Mihome controller")

        self.controller = Controller(self.core)

        return self.controller

    def stop_controller(self):

        if self.controller:

            self.log.info("stopping Mihome controller")
            self.controller.destroy()

            self.controller = None

    def controller_send(self, gatewayId, message, callback):

        if self.controller:

            gateway = self.core.get(gatewayId)

            if gateway:
                self.controller.sendData(gateway, message, callback=callback)
            else:
                raise Exception("no Mihome gateway with id = %s" % gatewayId)

        else:
            raise Exception("no Mihome controller launched")
