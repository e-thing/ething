# coding: utf-8

import paho.mqtt.client as mqttClient
import paho.mqtt.publish as publish
from ething.core.flow import *



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


@meta(icon='mdi-send')
@attr('qos', type=Enum([0,1,2]), default=0, description="the qos to use when publishing.")
@attr('payload', type=String(), default='', description="the payload to be published. If an empty string is given, a zero length payload will be published.")
@attr('password', type=String(), default='', description="password for the client. Leave empty to disable authentication.")
@attr('username', type=String(), default='', description="username for the client. Leave empty to disable authentication.")
@attr('port', type=Integer(min=0, max=65535), default=1883, description="the port to connect to the broker on.")
@attr('hostname', type=String(allow_empty=False), description="a string containing the address of the broker to connect to.")
@attr('topic', type=String(allow_empty=False), description="the topic string to which the payload will be published.")
class MqttPublish(Node):
    """ Publish a single message to a broker """

    INPUTS = ['default']

    def main(self, **inputs):

        auth = None

        if self.username and self.password:
            auth = {
                'username': self.username,
                'password': self.password
            }

        self.log.debug("publish: topic=%s hostname=%s port=%s" % (self.topic, self.hostname, self.port))

        publish.single(self.topic, self.payload, hostname=self.hostname, port=self.port, qos=self.qos, auth=auth)



