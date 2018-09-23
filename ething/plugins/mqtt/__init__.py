# coding: utf-8

from .MQTT import MQTT
from ething.core.plugin import Plugin
from ething.core.Process import Process
import paho.mqtt.client as mqttClient
import threading


class mqtt(Plugin):

    def load(self):
        super(mqtt, self).load()

        self.controllers = {}

        gateways = self.core.find(lambda r: r.isTypeof('MQTT'))

        for gateway in gateways:
            try:
                self._start_controller(gateway)
            except Exception as e:
                self.log.exception('unable to start the controller for the device %s' % gateway)

        self.core.signalDispatcher.bind('ResourceCreated', self._on_resource_created)
        self.core.signalDispatcher.bind('ResourceDeleted', self._on_resource_deleted)
        self.core.signalDispatcher.bind('ResourceUpdated', self._on_resource_updated)

    def unload(self):
        super(mqtt, self).unload()
        self.core.signalDispatcher.unbind('ResourceCreated', self._on_resource_created)
        self.core.signalDispatcher.unbind('ResourceDeleted', self._on_resource_deleted)
        self.core.signalDispatcher.unbind('ResourceUpdated', self._on_resource_updated)

        self.stop_all_controllers()

    def _on_resource_created(self, signal):
        device = signal.resource
        if isinstance(device, MQTT):
            self._start_controller(device)

    def _on_resource_deleted(self, signal):
        device = signal.resource
        if isinstance(device, MQTT):
            self._stop_controller(device.id)

    def _on_resource_updated(self, signal):
        id = signal.resource.id
        if id in self.controllers:
            controller = self.controllers[id]
            for attr in signal['attributes']:
                if attr in controller.RESET_ATTR:
                    self._stop_controller(id)
                    self._start_controller(controller.device)
                    break

    def _start_controller(self, device):
        controller = Controller(device)
        self.controllers[device.id] = controller
        controller.start()

    def _stop_controller(self, id):

        if id in self.controllers:
            controller = self.controllers[id]
            controller.stop()
            del self.controllers[id]

    def stop_all_controllers(self):
        if hasattr(self, 'controllers'):
            for id in list(self.controllers):
                self._stop_controller(id)


class Controller(Process):
    RESET_ATTR = ['port', 'host', 'auth', 'subscription']
    KEEPALIVE = 60  # seconds

    def __init__(self, gateway):
        super(Controller, self).__init__('mqtt.%s' % gateway.id)
        self.device = gateway
        self._lock = threading.Lock()

    def main(self):
        self._mqttClient = mqttClient.Client(client_id=self.device.id, clean_session=True)

        self._mqttClient.on_connect = self.on_connect
        self._mqttClient.on_message = self.on_message
        self._mqttClient.on_disconnect = self.on_disconnect

        self.log.info("MQTT: connecting to %s:%d" % (self.device.host, self.device.port))

        if self.device.auth:
            self._mqttClient.username_pw_set(self.device.auth['user'], password=self.device.auth['password'])

        self._mqttClient.connect(self.device.host, port=self.device.port, keepalive=self.KEEPALIVE)

        while not self.stopped():
            self._mqttClient.loop(1.0)

        self.log.info("MQTT: disconnect")
        self._mqttClient.disconnect()
        self.device.setConnectState(False)

    def on_connect(self, client, userdata, flags, rc):

        if rc == 0:
            self.log.info("MQTT: connected")

            self.device.setConnectState(True)

            # subscribe
            topics = []
            for item in self.device.getSubscription():
                topic = item['topic']
                self.log.info("MQTT: subscribing to topic %s" % topic)
                topics.append((topic, 0))

            if topics:
                self._mqttClient.subscribe(topics)

        else:
            # unable to connect
            self.log.error("MQTT: connection refused : %s" %
                           mqttClient.connack_string(rc))
            self.stop()

    def on_message(self, client, userdata, msg):
        self.log.debug("MQTT: new message for topic %s" % msg.topic)

        with self.device as device:
            device.setConnectState(True)

            try:
                device.processPayload(msg.topic, msg.payload)
            except Exception as e:
                self.log.error(e)

    def on_disconnect(self, client, userdata, rc):
        self.device.setConnectState(False)
        if rc != 0:
            self.log.warning("MQTT: Unexpected disconnection")
            self._mqttClient.reconnect()

    def publish(self, topic, payload, retain=False):
        with self._lock:
            self.log.debug("MQTT: publish to topic %s" % topic)
            self._mqttClient.publish(topic, payload, 0, retain)