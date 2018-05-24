# coding: utf-8
from future.utils import string_types

from .Controller import Controller
from .MySensorsGateway import MySensorsGateway, Device
from .MySensorsSerialGateway import MySensorsSerialGateway
from .MySensorsEthernetGateway import MySensorsEthernetGateway
from .MySensorsNode import MySensorsNode
from .MySensorsSensor import MySensorsSensor
from .helpers import *

import serial
import socket
try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse


class MySensors(object):

    def __init__(self, core):
        self.core = core
        self.log = core.log
        self.rpc = core.rpc

        self.controllers = {}

        self.rpc.register('device.mysensors.send',
                          self.controller_send, callback_name='callback')
        self.rpc.register('device.mysensors.sendWaitResponse',
                          self.controller_send_wait_response, callback_name='callback')
        self.rpc.register('device.mysensors.updateFirmware',
                          self.controller_update_firmware, callback_name='callback')

        self.core.signalManager.bind(
            'ResourceCreated', self.on_resource_created)
        self.core.signalManager.bind(
            'ResourceDeleted', self.on_resource_deleted)

        devices = self.core.find({
            'type': {'$regex': '^MySensors.*Gateway$'}
        })

        for device in devices:
            try:
                self.start_controller(device)
            except Exception as e:
                self.log.error(e)

    def on_resource_created(self, signal):
        device = self.core.get(signal['resource'])
        if isinstance(device, MySensorsGateway):
            self.start_controller(device)

    def on_resource_deleted(self, signal):
        device = self.core.get(signal['resource'])
        if isinstance(device, MySensorsGateway):
            self.stop_controller(device)

    def start_controller(self, device):

        if isinstance(device, string_types):
            device = self.core.get(device)

        if not device or not isinstance(device, MySensorsGateway):
            raise Exception(
                "the device %s does not exist or has the wrong type" % str(device))

        # remove any previous stream from this device
        self.stop_controller(device)

        self.log.info("starting MySensors controller '%s' id=%s type=%s" % (
            device.name, device.id, device.type))

        transport = None

        if isinstance(device, MySensorsSerialGateway):
            transport = SerialTransport
        elif isinstance(device, MySensorsEthernetGateway):
            transport = EthernetTransport
        else:
            raise Exception("no transport found")

        controller = Controller(device, transport)

        self.controllers[device.id] = controller

        return controller

    def stop_controller(self, device):

        if isinstance(device, Device):
            device = device.id

        if device in self.controllers:
            controller = self.controllers[device]
            self.log.info("stopping MySensors controller '%s' id=%s type=%s" % (
                controller.gateway.name, controller.gateway.id, controller.gateway.type))
            controller.destroy()
            del self.controllers[device]

    def stop_all_controllers(self):
        for id in list(self.controllers):
            self.stop_controller(id)
        self.controllers = {}

    def controller_send(self, gatewayId, message, callback):

        if gatewayId in self.controllers:

            controller = self.controllers[gatewayId]

            controller.send(message, callback=callback)

        else:
            raise Exception(
                "unknown MySensors instance for device id %s" % gatewayId)

    def controller_send_wait_response(self, gatewayId, message, callback):

        if gatewayId in self.controllers:

            controller = self.controllers[gatewayId]

            controller.send(message, callback=callback, waitResponse=True)

        else:
            raise Exception(
                "unknown MySensors instance for device id %s" % gatewayId)

    def controller_update_firmware(self, node_id, firmware, callback=None):

        node = self.core.get(node_id)
        if node:
            gateway = node.gateway
            if gateway:

                if gateway.id in self.controllers:
                    controller = self.controllers[gateway.id]

                    controller.updateFirmware(node, firmware, callback)

                else:
                    raise Exception(
                        "unknown MySensors instance for device id %s" % gateway.id)
            else:
                raise Exception(
                    "unable to find gateway for node %s" % str(node))
        else:
            raise Exception("unknown MySensors node with id = %s" % node_id)


class SerialTransport(object):

    def __init__(self, controller):
        self._buffer = b""
        self._serial = None
        self._controller = controller
        self._socketManager = controller.ething.socketManager
        self.log = controller.log

    def open(self):

        self._buffer = b""

        port = self._controller.gateway.port
        baudrate = self._controller.gateway.baudrate

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

    def write(self, message):
        if self._serial:
            return self._serial.write(message.raw() + b"\n")
        else:
            return 0

    def read(self):
        if self._serial:
            chunk = self._serial.read(1024)  # return as bytes

            if not chunk:
                self.log.warn("[serial]: link broken... close")
                self._controller.close()
                return None

            return chunk
        else:
            return None

    def readlines(self):
        l = []
        chunk = self.read()
        if chunk:
            self._buffer += chunk

            while True:
                p = self._buffer.find(b"\n")
                if p >= 0:
                    line = self._buffer[0:p]
                    self._buffer = self._buffer[p+1:]
                    l.append(line.rstrip())
                else:
                    break

        return l

    def onRead(self):
        for line in self.readlines():
            try:
                self._controller.processMessage(line)
            except Exception as e:
                # skip the line
                self.log.exception(
                    "[serial]: unable to handle the message %s" % line)


class EthernetTransport(object):

    def __init__(self, controller):
        self._buffer = b""
        self._sock = None
        self._controller = controller
        self._socketManager = controller.ething.socketManager
        self.log = controller.log

    def open(self):

        self._buffer = b""

        o = urlparse('tcp://'+self._controller.gateway.address)

        # open socket
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self._sock.connect((o.hostname, o.port))
        self._sock.setblocking(0)

        self._socketManager.registerReadSocket(self._sock, self.onRead)

        self.log.info(
            "[Ethernet]: connection opened, host: %s , port: %d" % (o.hostname, o.port))

        return True

    def close(self):
        if self._sock:
            self._socketManager.unregisterReadSocket(self._sock)
            self._sock.close()
            self._sock = None
            self.log.info("[Ethernet]: port closed")

    def write(self, message):
        if self._sock:
            return self._sock.send(message.raw() + b"\n")
        else:
            return 0

    def read(self):
        if self._sock:
            chunk = self._sock.recv(1024)  # return as bytes

            if not chunk:
                self.log.warn("[Ethernet]: empty string received... close")
                self._controller.close()
                return None

            return chunk
        else:
            return None

    def readlines(self):
        l = []
        chunk = self.read()
        if chunk:
            self._buffer += chunk

            while True:
                p = self._buffer.find(b"\n")
                if p >= 0:
                    line = self._buffer[0:p]
                    self._buffer = self._buffer[p+1:]
                    l.append(line.rstrip())
                else:
                    break

        return l

    def onRead(self):
        for line in self.readlines():
            try:
                self._controller.processMessage(line)
            except Exception as e:
                # skip the line
                self.log.exception(
                    "[Ethernet]: unable to handle the message %s" % line)
