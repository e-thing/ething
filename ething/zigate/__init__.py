# coding: utf-8
from future.utils import string_types, bchr, bord

from .Controller import Controller
from .ZigateGateway import ZigateGateway, Device
from .ZigateSerialGateway import ZigateSerialGateway
from .ZigateAqaraTHP import ZigateAqaraTHP
from .Message import Message

import serial
import binascii


class Zigate(object):

    def __init__(self, core):
        self.core = core
        self.log = core.log
        self.rpc = core.rpc

        self.controllers = {}

        self.rpc.register('device.zigate.send',
                          self.controller_send, callback_name='callback')

        self.core.signalManager.bind(
            'ResourceCreated', self.on_resource_created)
        self.core.signalManager.bind(
            'ResourceDeleted', self.on_resource_deleted)

        devices = self.core.find(lambda r: r.isTypeof('resources/ZigateGateway'))

        for device in devices:
            try:
                self.start_controller(device)
            except Exception as e:
                self.log.error(e)

    def on_resource_created(self, signal):
        device = signal.resource
        if isinstance(device, ZigateGateway):
            self.start_controller(device)

    def on_resource_deleted(self, signal):
        device = signal.resource
        if isinstance(device, ZigateGateway):
            self.stop_controller(device)

    def start_controller(self, device):

        if isinstance(device, string_types):
            device = self.core.get(device)

        if not device or not isinstance(device, ZigateGateway):
            raise Exception(
                "the device %s does not exist or has the wrong type" % str(device))

        # remove any previous stream from this device
        self.stop_controller(device)

        self.log.info("starting Zigate controller '%s' id=%s type=%s" %
                      (device.name, device.id, device.type))

        controller = Controller(device, SerialTransport)

        self.controllers[device.id] = controller

        return controller

    def stop_controller(self, device):

        if isinstance(device, Device):
            device = device.id

        if device in self.controllers:
            controller = self.controllers[device]
            self.log.info("stopping Zigate controller '%s' id=%s type=%s" % (
                controller.gateway.name, controller.gateway.id, controller.gateway.type))
            controller.destroy()
            del self.controllers[device]

    def stop_all_controllers(self):
        for id in list(self.controllers):
            self.stop_controller(id)
        self.controllers = {}

    def controller_send(self, gatewayId, message, waitResponse=None, callback=None):

        if gatewayId in self.controllers:

            controller = self.controllers[gatewayId]

            controller.send(message, callback=callback,
                            waitResponse=waitResponse)

        else:
            raise Exception(
                "unknown Zigate instance for device id %s" % gatewayId)


class SerialTransport(object):

    def __init__(self, controller):
        self._buffer = b""
        self._serial = None
        self._controller = controller
        self._socketManager = controller.ething.socketManager
        self.log = controller.log
        self._transcodage = False

    def open(self):

        self._buffer = b""
        self._transcodage = False

        port = self._controller.gateway.port
        baudrate = 115200

        # open serial port
        self._serial = serial.Serial(port, baudrate, timeout=0)

        self._socketManager.registerReadSocket(self._serial, self.onRead)

        self.log.info("[serial]: port opened : %s baudrate: %d" %
                      (port, baudrate))

        return True

    def close(self):
        if self._serial:
            self._socketManager.unregisterReadSocket(self._serial)
            self._serial.close()
            self._serial = None
            self.log.info("[serial]: port closed")

    def write(self, data):
        if self._serial:
            return self._serial.write(data)
        else:
            return 0

    def read(self):
        if self._serial:
            chunk = self._serial.read(1024)  # return as bytes

            if not chunk:
                self.log.warning("[serial]: link broken... close")
                self._controller.close()
                return None

            return chunk
        else:
            return None

    def onRead(self):
        chunk = self.read()
        if chunk:

            for b in chunk:
                o = bord(b)
                if o == 1:
                    self._buffer = b''
                elif o == 3:
                    try:
                        message = Message.parse(
                            b"01"+binascii.hexlify(self._buffer)+b"03")
                        self._controller.processMessage(message)
                    except Exception as e:
                        # skip the line
                        self.log.exception(
                            "[serial]: unable to handle the message %s" % self._buffer)
                    self._buffer = ''
                elif o == 2:
                    self._transcodage = True
                else:
                    if self._transcodage:
                        o = o ** 0x10
                        self._transcodage = False

                    self._buffer += bchr(o)
