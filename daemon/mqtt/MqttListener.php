<?php

use \Ething\Ething;
use \Ething\MQTT\phpMQTT;


class MqttListener extends Stream {
	
	
	const AUTOCONNECT_PERIOD = 15; // seconds
	const KEEPALIVE = 60; // seconds
	
	protected $stream = null;
	
	protected $status;
	protected $mqttClient = null;
	
	private $lastAutoconnectLoop = 0;
	
	public $ething;
	
	protected $host;
	protected $port;
	protected $clientId;
	protected $rootTopic = '';
	
	protected $onMessage = null;
	
	public function __construct(Ething $ething, $cleanSession = false) {
		$this->status = "disconnected";
		$this->ething = $ething;
		
		$mqttSettings = $this->ething->config('mqtt');
		
		if(empty($mqttSettings) || !isset($mqttSettings['host']) || !isset($mqttSettings['port'])){
			throw new \Exception('mqtt feature disabled');
		}
		
		$this->host = $mqttSettings['host'];
		$this->port = $mqttSettings['port'];
		$this->clientId = isset($mqttSettings['clientId']) && !empty($mqttSettings['clientId']) ? $mqttSettings['clientId'] : uniqid();
		if(isset($mqttSettings['rootTopic']) && is_string($mqttSettings['rootTopic'])) {
			$this->rootTopic = $mqttSettings['rootTopic']; // must end with an '/'
		}
		
		$this->mqttClient = new phpMQTT($this->host, $this->port, $this->clientId);
		$this->mqttClient->keepalive = self::KEEPALIVE;
		
	}
	
	public function onMessage($callback) {
		if(is_callable($callback) || is_null($callback)){
			$this->onMessage = $callback;
		}
	}
	
	public function processMessage($topic, $message) {
		//echo "MQTT(server): new message for topic {$topic} : {$message}\n";
		//Log::debug("MQTT(server): new message for topic {$topic}");
		
		// remove the root part ! The topic must be relative to this root topic
		$offset = strlen($this->rootTopic);
		if($offset) $topic = substr($topic, $offset);
		
		if($this->onMessage!==null){
			call_user_func($this->onMessage, $topic, $message);
		}
		
	}
	
	public function reset(){
		$this->disconnect();
		$this->lastAutoconnectLoop = 0;
		// auto reconnect as soon as possible
	}
	
	public function connect(){
		$this->disconnect();
		$this->mqttClient->broker($this->host, $this->port, $this->clientId);
		
		Log::info("MQTT(server): connecting to {$this->host}:{$this->port}");
		
		$clean = true; // If the clean session is set to true then the client does not have a persistent session and all information are lost when the client disconnects for any reason. When clean session is set to false, a persistent session is created and it will be preserved until the client requests a clean session again. If there is already a session available then it is used and queued messages will be delivered to the client if available.
		$will = null; // array ( 'topic' => ? , 'content' => ? , 'qos' => ? , 'retain' => ? ) 
		$username = null;
		$password = null;
		
//		if(isset($this->device->auth)){
//			$username = $this->device->auth['user'];
//			$username = $this->device->auth['password'];
//		}
		
		if($this->mqttClient->connect($clean, $will, $username, $password)){
			
			$topic = $this->toAbsoluteTopic('#');
			
			Log::info("MQTT(server): connected");
			
			Log::info("MQTT(server): subscribing to {$topic}");
			
			$topics = array();
			$topics[$topic] = array("qos"=>0, "function"=>array($this, 'processMessage'));
			$this->mqttClient->subscribe($topics,0);
			
			$this->stream = $this->mqttClient->getSocket();
			
			Log::info("MQTT(server): subscribed");
			
			$this->status = "connected";
			return true;
		}
		
		return false;
	}
	
	public function disconnect(){
		if($this->status !== "disconnected"){
			Log::info("MQTT(server): disconnect");
			$this->mqttClient->close();
			$this->stream = null;
			$this->status = "disconnected";
		}
	}
	
	public function getStatus(){
		return $this->status;
	}
	
	public function read(){
		return $this->update();
	}
	
	public function close(){
		return $this->disconnect();
	}
	
	public function update() {
		
		$now = microtime(true);
		
		// auto connect
		if($this->status === "disconnected" && ($now - $this->lastAutoconnectLoop) > self::AUTOCONNECT_PERIOD ){
			$this->lastAutoconnectLoop = $now;
			$this->connect();
		}
		
		if($this->status === "connected"){
			if(!$this->mqttClient->proc()){
				// disconnected !
				Log::info("MQTT(server): disconnected by the host");
				
				$this->stream = null;
				$this->status = "disconnected";
				$this->lastAutoconnectLoop = 0;
				// auto reconnect as soon as possible
			}
		}
	
	}
	
	public function publish($topic, $payload, $retain = false){
		
		if($this->status === "connected"){
			
			if(empty($topic)){
				throw new \Exception("topic is an empty string");
			}
			
			$topic = $this->toAbsoluteTopic($topic);
			
			Log::debug("MQTT(server): publish to topic {$topic}");
			
			if(!is_string($payload)){
				$payload = \json_encode($payload);
			}
			
			$this->mqttClient->publish($topic,$payload,0,$retain);
			
			return true;
		}
		
		return false;
	}
	
	private function toAbsoluteTopic($topic){
		$t = $this->rootTopic;
		if(strlen($t) && substr($t, -1)!=='/') $t.='/';
		$t.=$topic;
		return $t;
	}
	
	public function getStream(){
		return $this->stream;
	}
	
	public function process(){
		$this->read();
	}
}
