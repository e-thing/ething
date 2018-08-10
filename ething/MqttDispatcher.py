# coding: utf-8

from .plugin import Plugin
from .Process import Process
import threading
import paho.mqtt.client as mqttClient
from ething.event import ResourceSignal
import random
import string
import time
from ething.Helpers import toJson
from collections import OrderedDict


class MqttDispatcher(Plugin):
    CONFIG_DEFAULTS = {
        'port': 1883,
    }

    CONFIG_SCHEMA = {
        'type': 'object',
        'properties': OrderedDict([
            ('host', {
                'description': 'leave empty to disable this plugin',
                'type': 'string',
                'minLength': 1
            }),
            ('port', {
                'type': 'integer',
                'minimum': 1,
                'maximum': 65535
            }),
            ('user', {
                'type': 'string',
                'minLength': 1
            }),
            ('password', {
                'type': 'string',
                'minLength': 4
            })
        ])
    }

    def load(self):
        super(MqttDispatcher, self).load()
        self.start_process()

    def unload(self):
        super(MqttDispatcher, self).unload()
        self.stop_process()

    def start_process(self):
        if self.config.get('host'):
            self.process = MqttDispatcherService(self.core, self.config)
            self.process.start()

    def stop_process(self):
        if hasattr(self, 'process'):
            self.process.stop()
            del self.process

    def on_config_change(self, changes):
        self.stop_process()
        self.start_process()



class MqttDispatcherService(Process):

    KEEPALIVE = 60  # seconds
    RECONNECT_DELAY = 30

    def __init__(self, core, config):
        super(MqttDispatcherService, self).__init__('mqttDispatcher')
        self.core = core
        self.config = config
        self._lock = threading.Lock()

    def main(self):
        self._mqttClient = mqttClient.Client(client_id='ething_%s' % ''.join(random.choice(
            string.ascii_uppercase + string.digits) for _ in range(6)), clean_session=True)

        self._mqttClient.on_connect = self.on_connect
        self._mqttClient.on_disconnect = self.on_disconnect

        host = self.config.get('host')
        port = self.config.get('port', 1883)

        user = self.config.get('user')
        password = self.config.get('password')
        if user and password:
            self._mqttClient.username_pw_set(user, password=password)

        while not self.stopped():

            try:
                self._mqttClient.connect(host, port=port, keepalive=self.KEEPALIVE)
            except Exception as e:
                # unable to connect
                self.log.error("Error: unable to connect to %s:%d" % (host, port))
                # wait before retry
                t_end = time.time() + self.RECONNECT_DELAY
                while not self.stopped() and time.time() < t_end:
                    time.sleep(0.5)
                continue

            self.log.info("connected to %s:%d" % (host, port))

            while not self.stopped():
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
            topic += '/%s' % signal.resource

        payload = toJson(signal)

        self.log.debug("publish topic=%s" % topic)

        self.mqttClient.publish(topic, payload, 0, True)






