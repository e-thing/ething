# coding: utf-8

from ething.core.plugin import *
from ething.core.Process import Process
import threading
import paho.mqtt.client as mqttClient
from ething.core.Signal import ResourceSignal
import random
import string
import time
from ething.core.Helpers import toJson
from collections import OrderedDict


@attr('password', type=String(password=True), default='')
@attr('user', type=String(), default='')
@attr('port', type=Number(min=1, max=65535), default=1883)
@attr('host', type=String(), default='', description='leave empty to disable this plugin')
class MqttDispatcher(Plugin):

    def setup(self):
        self.service = None
        self.update_service()

    def on_config_change(self, dirty_attributes):
        self.update_service()

    def update_service(self):
        if self.service is not None:
            self.service.stop()
            self.service = None
        if self.host:
            self.service = MqttDispatcherService(self.core, self.host, self.port, self.user, self.password)
            self.core.process_manager.attach(self.service)


class MqttDispatcherService(Process):

    KEEPALIVE = 60  # seconds
    RECONNECT_DELAY = 30

    def __init__(self, core, host, port=1883, user=None, password=None):
        super(MqttDispatcherService, self).__init__(name='mqttDispatcher')
        self.core = core
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self._lock = threading.Lock()

    def main(self):
        self._mqttClient = mqttClient.Client(client_id='ething_%s' % ''.join(random.choice(
            string.ascii_uppercase + string.digits) for _ in range(6)), clean_session=True)

        self._mqttClient.on_connect = self.on_connect
        self._mqttClient.on_disconnect = self.on_disconnect

        host = self.host
        port = self.port

        user = self.user
        password = self.password
        if user and password:
            self._mqttClient.username_pw_set(user, password=password)

        while self.is_running:

            try:
                self._mqttClient.connect(host, port=port, keepalive=self.KEEPALIVE)
            except Exception as e:
                # unable to connect
                self.log.error("Error: unable to connect to %s:%d" % (host, port))
                # wait before retry
                t_end = time.time() + self.RECONNECT_DELAY
                while self.is_running and time.time() < t_end:
                    time.sleep(0.5)
                continue

            self.log.info("connected to %s:%d" % (host, port))

            while self.is_running:
                self._mqttClient.loop(1.0)

            self.log.info("disconnect")
            self._mqttClient.disconnect()

    def on_connect(self, client, userdata, flags, rc):

        if rc == 0:
            self.log.info("connected")

            self.core.signalDispatcher.bind('*', self.dispatchSignal)

        else:
            # unable to connect
            self.log.error("connection refused : %s" %
                           mqttClient.connack_string(rc))
            self.stop()

    def on_disconnect(self, client, userdata, rc):
        if rc != 0:
            self.log.warning("Unexpected disconnection")
            self._mqttClient.reconnect()

        self.core.signalDispatcher.unbind('*', self.dispatchSignal)

    def dispatchSignal(self, signal):

        signal_type = type(signal).__name__

        topic = 'event/%s' % signal_type

        if isinstance(signal, ResourceSignal):
            topic += '/%s' % signal.resource.id

        payload = toJson(signal)

        self.log.debug("publish topic=%s" % topic)

        self.mqttClient.publish(topic, payload, 0, True)






