
import paho.mqtt.client as mqttClient
from ething.event import ResourceSignal
import random
import string
from ething.Helpers import toJson



class MqttDispatcher(object):
    """
    dispatch signals over MQTT
    """
    
    AUTOCONNECT_PERIOD = 15
    
    def __init__(self, core):
        self.core = core
        self.log = core.log
        self.socketManager = core.socketManager
        
        self._socket = None
        
        self.mqttClient = mqttClient.Client( client_id = 'ething_%s' % ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6)), clean_session = True) 
        self.mqttClient.on_connect= self.on_connect
        self.mqttClient.on_disconnect = self.on_disconnect
        
        self.core.scheduler.setInterval(1,self.update)
        
        self.connect()
    
    
    def destroy(self):
        self.disconnect()
    
    
    def dispatchSignal(self, signal):
        
        signal_type = type(signal).__name__
        
        topic = 'event/%s' % signal_type
        
        if isinstance(signal, ResourceSignal):
            topic += '/%s' % signal.resource
        
        payload = toJson(signal.__dict__)
        
        self.log.debug("MqttDispatcher: publish topic=%s" % (topic))
        
        self.mqttClient.publish(topic, payload, 0, True)
        
        self.processWrite()
    
    
    def connect(self):
        
        host = self.core.config.get('mqtt.host')
        port = self.core.config.get('mqtt.port', 1883)
        
        if not host:
            return
        
        self.log.info("MqttDispatcher: connecting to %s:%d" % (host,port))
        
        user = self.core.config.get('mqtt.user')
        password = self.core.config.get('mqtt.password')
        if user and password:
            self.mqttClient.username_pw_set(user, password=password)
        
        self.mqttClient.connect(host, port=port, keepalive=60)
        
        self._socket = self.mqttClient.socket()
        self.socketManager.registerReadSocket(self._socket, self.process)
        
        self.processWrite()
    
    
    def disconnect(self):
        self.log.info("MqttDispatcher: disconnect")
        self.mqttClient.disconnect()
    
    def on_connect(self, client, userdata, flags, rc):
        
        if rc == 0:
            self.log.info("MqttDispatcher: connected")
            
            self.core.signalManager.addDispatcher(self.dispatchSignal)
            
        else:
            # unable to connect
            self.log.error("MqttDispatcher: connection refused : %s, reconnecting in %d secondes" % mqttClient.connack_string(rc))
            self.core.scheduler.delay(self.AUTOCONNECT_PERIOD, self.connect)
            
    
    def on_disconnect(self, client, userdata, rc):
        if rc != 0:
            self.log.warn("MqttDispatcher: Unexpected disconnection, reconnecting in %d secondes" % self.AUTOCONNECT_PERIOD)
            self.core.scheduler.delay(self.AUTOCONNECT_PERIOD, self.connect)
        
        self.socketManager.unregisterReadSocket(self._socket)
        self.socketManager.unregisterWriteSocket(self._socket)
        self.core.signalManager.removeDispatcher(self.dispatchSignal)
    
    
    
    def process(self):
        self.mqttClient.loop_read()
        self.processWrite()
    
    def processWrite(self):
        if self.mqttClient.want_write():
            self.socketManager.registerWriteSocketOnce(self._socket, self.mqttClient.loop_write)
    
    
    def update (self):
        self.mqttClient.loop_misc()
        
        self.processWrite()
            