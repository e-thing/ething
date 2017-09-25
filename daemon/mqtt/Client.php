<?php

namespace Ething\MQTT;

use \Ething\Device\MQTT;
use \Ething\MQTT\phpMQTT;
use \Ething\Exception;

class Client extends \Stream {
	
	
	const AUTOCONNECT_PERIOD = 15; // seconds
	const KEEPALIVE = 60; // seconds
	
	protected $stream = null;
	
	protected $status;
	protected $mqttClient = null;
	
	protected $logger;
	
	private $lastAutoconnectLoop = 0;
	
	public $device = null;
	
	public $subscribeMode;
	
	public function __construct(MQTT $device, $cleanSession = false) {
		$this->status = "disconnected";
		$this->device = $device;
		$this->subscribeMode = isset($this->device->topic);
		
		$this->mqttClient = new phpMQTT($this->device->host, $this->device->port, (string)$this->device->id());
		$this->mqttClient->keepalive = self::KEEPALIVE;
		
		$this->logger = $device->ething->logger();
	}
	
	public function processMessage($topic, $message) {
		$this->logger->debug("MQTT: new message for topic {$topic}");
		try {
			$this->device->processMessage($topic, $message);
		} catch (\Exception $e) {} // skip any error
	}
	
	public function reset(){
		$this->disconnect();
		$this->lastAutoconnectLoop = 0;
		// auto reconnect as soon as possible
	}
	
	public function connect(){
		$this->disconnect();
		$this->mqttClient->broker($this->device->host, $this->device->port, (string)$this->device->id());
		
		$this->logger->info("MQTT: connecting to {$this->device->host}:{$this->device->port}");
		
		$clean = true; // If the clean session is set to true then the client does not have a persistent session and all information are lost when the client disconnects for any reason. When clean session is set to false, a persistent session is created and it will be preserved until the client requests a clean session again. If there is already a session available then it is used and queued messages will be delivered to the client if available.
		$will = null; // array ( 'topic' => ? , 'content' => ? , 'qos' => ? , 'retain' => ? ) 
		$username = null;
		$password = null;
		
		if(isset($this->device->auth)){
			$username = $this->device->auth['user'];
			$password = $this->device->auth['password'];
		}
		
		if($this->mqttClient->connect($clean, $will, $username, $password)){
			
			$this->logger->info("MQTT: connected");
			
			if(isset($this->device->topic)){
				$this->logger->info("MQTT: subscribing to {$this->device->topic}");
				
				$topics = array();
				$topics[$this->device->topic] = array("qos"=>0, "function"=>array($this, 'processMessage'));
				$this->mqttClient->subscribe($topics,0);
				
				$this->stream = $this->mqttClient->getSocket();
				
				$this->logger->info("MQTT: subscribed");
			}
			
			$this->device->updateSeenDate();
			
			$this->status = "connected";
			return true;
		}
		
		return false;
	}
	
	public function disconnect(){
		if($this->status !== "disconnected"){
			$this->logger->info("MQTT: disconnect");
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
		if($this->status === "disconnected" && ($now - $this->lastAutoconnectLoop) > self::AUTOCONNECT_PERIOD && $this->subscribeMode ){
			$this->lastAutoconnectLoop = $now;
			$this->connect();
		}
		
		if($this->status === "connected"){
			if(!$this->mqttClient->proc()){
				// disconnected !
				$this->logger->info("MQTT: disconnected by the host");
				
				$this->stream = null;
				$this->status = "disconnected";
				$this->lastAutoconnectLoop = 0;
				// auto reconnect as soon as possible
			}
		}
	
	}
	
	public function publish($topic, $payload, $retain = false){
		
		if(!$this->subscribeMode){
			$this->connect();
		}
		
		if($this->status === "connected"){
			$this->logger->debug("MQTT: publish to topic {$topic}");
			
			if(empty($topic)){
				throw new \Exception("topic is an empty string");
			}
			
			$this->mqttClient->publish($topic, $payload, 0, $retain);
			
			if(!$this->subscribeMode){
				$this->disconnect();
			}
			
			return true;
		}
		
		return false;
	}
	
	
	public function getStreams(){
		return array($this->stream);
	}
	
	public function process($stream){
		$this->read();
	}
}
