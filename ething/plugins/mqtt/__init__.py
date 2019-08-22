# coding: utf-8

from ething.plugin import *
import paho.mqtt.client as mqttClient
import paho.mqtt.publish as publish
from ething.flow import *
from ething.TransportProcess import Transport
import json
from queue import Queue, Empty
from .dispatcher import MqttDispatcherService


@attr('publish_event', label="publish event", type=Dict(mapping=[
    {
        'name': 'enable',
        'type': Boolean(),
    },
    {
        'name': 'base_topic',
        'label': 'base topic',
        'type': String(),
        'description': 'The prefix for the event topic'
    },
], optionals=['base_topic']), default={
    'enable': False,
    'base_topic': 'ething'
}, description="If enable, the events will be published to the MQTT broker.")
@attr('password', type=String(password=True), default='')
@attr('user', type=String(), default='')
@attr('port', type=Number(min=1, max=65535), default=1883)
@attr('host', type=String(), default='', description='leave empty to disable this plugin')
class Mqtt(Plugin):

    def setup(self):
        self.service = None
        self.update_service()

    def on_config_change(self, dirty_attributes):
        self.update_service()

    def update_service(self):
        if self.service is not None:
            self.service.stop()
            self.service = None
        if self.host and self.publish_event.get('enable'):
            self.service = MqttDispatcherService(self.core, self.host, self.port, self.user, self.password, self.publish_event.get('base_topic'))
            self.core.processes.add(self.service)


class MqttTransport(Transport):

    def __init__(self, host, topic, port=1883, username=None, password=None, qos=0, connection_timeout=5):
        super(MqttTransport, self).__init__()
        self.host = host
        self.port = port
        self.topic = topic
        self.username = username
        self.password = password
        self.qos = qos
        self.connection_timeout = connection_timeout
        self._q_msg = Queue()
        self._c = mqttClient.Client()

        if self.username and self.password:
            self._c.username_pw_set(self.username, self.password)

        self._c.on_message = self.on_message
        self._c.on_connect = self.on_connect
        self._c.on_disconnect = self.on_disconnect

    def open(self):
        self._connected = False
        self._connect_error = False

        self._c.connect(self.host, port=self.port)

        t0 = time.time()
        while self._connected is False and self._connect_error is False and (time.time() - t0) < self.connection_timeout:
            self._c.loop(timeout=0.2, max_packets=1)

        if self._connect_error is not False:
            raise Exception('mqtt: unable to connect rc=%d' % self._connect_error)

        if not self._connected:
            raise Exception('mqtt: connect timeout')

        self._c.subscribe(self.topic, self.qos)

        super(MqttTransport, self).open()
        self.log.info("(mqtt) connected to host=%s port=%d" % (self.host, self.port))

    def on_message(self, client, userdata, msg):
        # msg.topic
        # msg.payload
        self._q_msg.put(msg)

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            # success
            self._connected = True
        else:
            # error
            self._connect_error = rc

    def on_disconnect(self, client, userdata, rc):
        self._connected = False
        if rc == 0:
            # disconnect was called !
            pass
        else:
            # need to reconnect
            self.close()

    def read(self):
        try:
            msg = self._q_msg.get(block=False)
        except Empty:
            self._c.loop(timeout=1.0, max_packets=1)
        else:
            return msg # msg = dict(topic, payload)

    def write(self, msg):
        # msg = dict(topic, payload=None, qos=0, retain=False)
        self._c.publish(msg)

    def close(self):
        super(MqttTransport, self).close()
        if self._connected:
            self._c.disconnect()

            t0 = time.time()
            while self._connected is True and (time.time() - t0) < self.connection_timeout:
                self._c.loop(timeout=0.2, max_packets=1)

            self.log.info("(net) closed from host=%s port=%d" % (self.host, self.port))


@meta(icon='mdi-signal-variant', category="input")
@attr('qos', type=Enum([0,1,2]), default=0, description="the quality of service.")
@attr('password', type=String(), default='', description="password for the client. Leave empty to disable authentication.")
@attr('username', type=String(), default='', description="username for the client. Leave empty to disable authentication.")
@attr('port', type=Integer(min=0, max=65535), default=1883, description="the port to connect to the broker on.")
@attr('hostname', type=String(allow_empty=False), description="a string containing the address of the broker to connect to.")
@attr('topic', type=String(allow_empty=False), description="the topic string to subscribe to.")
class MqttSubscribe(Node):
    OUTPUTS = ['default']

    def main(self, **inputs):

        def on_message(client, userdata, msg):
            self.emit({
                'topic': msg.topic,
                'payload': msg.payload
            })

        _mqttClient = mqttClient.Client()
        #_mqttClient.enable_logger(self.log)

        if self.username and self.password:
            _mqttClient.username_pw_set(self.username, self.password)

        _mqttClient.on_message = on_message

        _mqttClient.connect(self.hostname, port=self.port)

        _mqttClient.subscribe(self.topic, self.qos)

        _mqttClient.loop_forever()


@meta(icon='mdi-send', category="output")
@attr('qos', type=Enum([0,1,2]), default=0, description="the qos to use when publishing.")
@attr('payload', type=Descriptor(('msg', 'flow', 'glob', 'string', 'number', 'boolean', 'timestamp', 'env', 'template', 'expression')), default={'type':'msg','value':'payload'}, description='the payload to be published. If an empty string is given, a zero length payload will be published.')
@attr('password', type=String(), default='', description="password for the client. Leave empty to disable authentication.")
@attr('username', type=String(), default='', description="username for the client. Leave empty to disable authentication.")
@attr('port', type=Integer(min=0, max=65535), default=1883, description="the port to connect to the broker on.")
@attr('hostname', type=String(allow_empty=False), description="a string containing the address of the broker to connect to.")
@attr('topic', type=String(allow_empty=False), description="the topic string to which the payload will be published.")
class MqttPublish(Node):
    """ Publish a single message to a broker """

    INPUTS = ['default']

    def main(self, **inputs):
        _msg = inputs['default']
        _payload = self.payload.get(flow=self.flow, msg=_msg)

        auth = None

        if self.username and self.password:
            auth = {
                'username': self.username,
                'password': self.password
            }

        self.log.debug("publish: topic=%s hostname=%s port=%s", self.topic, self.hostname, self.port)

        if not isinstance(_payload, string_types):
            _payload = json.dumps(_payload)

        publish.single(self.topic, _payload, hostname=self.hostname, port=self.port, qos=self.qos, auth=auth)



