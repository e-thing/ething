# coding: utf-8


import paho.mqtt.client as _mqttClient
import time


class Controller(object):

    AUTOCONNECT_PERIOD = 15  # seconds
    KEEPALIVE = 60  # seconds

    reset_attr = ['port', 'host', 'auth', 'subscription']

    def __init__(self, device):
        self._status = "disconnected"
        self._device = device
        self._ething = device.ething

        self._log = device.ething.log

        self._autoreconnect = True
        self._nextConnect = 0

        self._socket = None

        self._mqttClient = _mqttClient.Client(
            client_id=self._device.id, clean_session=True)
        self._mqttClient.on_connect = self.on_connect
        self._mqttClient.on_message = self.on_message
        self._mqttClient.on_disconnect = self.on_disconnect

        # refresh the gateway each time the gateway properties changes
        self.ething.signalManager.bind(
            'ResourceMetaUpdated', self.onResourceMetaUpdated)

        self.ething.scheduler.tick(self.update)

    @property
    def device(self):
        return self._device

    @property
    def ething(self):
        return self._ething

    @property
    def log(self):
        return self._log

    @property
    def status(self):
        return self._status

    @property
    def client(self):
        return self._mqttClient

    def onResourceMetaUpdated(self, signal):
        if signal['resource'] == self.device.id:

            self.device.refresh()

            for attr in signal['attributes']:
                if attr in Controller.reset_attr:
                    self.restart()
                    break

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
                self.processWrite()

            self._status = "connected"

        else:
            # unable to connect
            self.log.error("MQTT: connection refused : %s" %
                           _mqttClient.connack_string(rc))
            self._status = "disconnected"
            self._nextConnect = time.time() + Controller.AUTOCONNECT_PERIOD

    def on_message(self, client, userdata, msg):
        self.log.debug("MQTT: new message for topic %s" % msg.topic)

        with self.device as device:
            device.setConnectState(True)

            try:
                device.processPayload(msg.topic, msg.payload)
            except Exception as e:
                self.log.error(e)

    def on_disconnect(self, client, userdata, rc):
        if rc != 0:
            self.log.warn("MQTT: Unexpected disconnection")

        self._status = "disconnected"
        self.device.setConnectState(False)
        self.ething.socketManager.unregisterReadSocket(self._socket)
        self.ething.socketManager.unregisterWriteSocket(self._socket)

    def restart(self):
        if self._status != "disconnected":
            self.close()
            self.open()

    def destroy(self):
        self.close()
        self.ething.signalManager.unbind(
            'ResourceMetaUpdated', self.onResourceMetaUpdated)

    def open(self):
        self.close()

        self.log.info("MQTT: connecting to %s:%d" %
                      (self.device.host, self.device.port))

        if self.device.auth:
            self._mqttClient.username_pw_set(
                self.device.auth['user'], password=self.device.auth['password'])

        self._status = "connecting"

        self._mqttClient.connect(
            self.device.host, port=self.device.port, keepalive=Controller.KEEPALIVE)

        self._socket = self._mqttClient.socket()

        self.ething.socketManager.registerReadSocket(
            self._socket, self.process)

        self.processWrite()

        return True

    def close(self):
        if self._status != "disconnected":
            self.log.info("MQTT: disconnect")
            self._mqttClient.disconnect()
            self._status = "disconnected"
            self.ething.socketManager.unregisterReadSocket(self._socket)
            self.ething.socketManager.unregisterWriteSocket(self._socket)
            self.device.setConnectState(False)

    def process(self):
        self._mqttClient.loop_read()
        self.processWrite()

    def processWrite(self):
        if self._mqttClient.want_write():
            self.ething.socketManager.registerWriteSocketOnce(
                self._socket, self._mqttClient.loop_write)

    def update(self):

        now = time.time()

        # auto connect
        if self._status == "disconnected" and self._autoreconnect is True and (now > self._nextConnect):
            self.open()

        if self._status != "disconnected":

            self._mqttClient.loop_misc()

            self.processWrite()

    def publish(self, topic, payload, retain=False):
        if self._status == "connected":
            self.log.debug("MQTT: publish to topic %s" % topic)
            self._mqttClient.publish(topic, payload, 0, retain)

            self.processWrite()

            return True
        return False
