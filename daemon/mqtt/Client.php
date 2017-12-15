<?php

namespace Ething\MQTT;

use \Ething\Device\MQTT;
use \Ething\MQTT\phpMQTT;
use \Ething\Exception;

class Client extends \Stream {
	
	
	const AUTOCONNECT_PERIOD = 15; // seconds
	const KEEPALIVE = 60; // seconds
	
	protected $status;
	protected $mqttClient = null;
	
	private $lastAutoconnectLoop = 0;
	
	public $device = null;
	
	public $subscribeMode;
	
	public function __construct(MQTT $device, $cleanSession = false) {
		$this->status = "disconnected";
		$this->device = $device;
		$this->subscribeMode = !empty($this->device->getSubscription());
		
		$this->mqttClient = new phpMQTT($this->device->host, $this->device->port, (string)$this->device->id());
		$this->mqttClient->keepalive = self::KEEPALIVE;
	}
	
	public function processMessage($topic, $message) {
		\Log::debug("MQTT: new message for topic {$topic}");
		try {
			$this->device->processPayload($topic, $message);
		} catch (\Exception $e) {
			\Log::error($e);
		} // skip any error
	}
	
	public function reset(){
		$this->disconnect();
		$this->lastAutoconnectLoop = 0;
		// auto reconnect as soon as possible
	}
	
	public function connect(){
		$this->disconnect();
		//$this->mqttClient->broker($this->device->host, $this->device->port, (string)$this->device->id());
		
		\Log::info("MQTT: connecting to {$this->device->host}:{$this->device->port}");
		
		$clean = true; // If the clean session is set to true then the client does not have a persistent session and all information are lost when the client disconnects for any reason. When clean session is set to false, a persistent session is created and it will be preserved until the client requests a clean session again. If there is already a session available then it is used and queued messages will be delivered to the client if available.
		$will = null; // array ( 'topic' => ? , 'content' => ? , 'qos' => ? , 'retain' => ? ) 
		$username = null;
		$password = null;
		
		if(isset($this->device->auth)){
			$username = $this->device->auth['user'];
			$password = $this->device->auth['password'];
		}
		
		if($this->mqttClient->connect($clean, $will, $username, $password)){
			
			\Log::info("MQTT: connected");
			
			$this->device->updateSeenDate();
			$this->device->setConnectState(true);
			
			// subscribe
			$topics = array();
			foreach($this->device->getSubscription() as $item){
				$topic = $item['topic'];
				\Log::info("MQTT: subscribing to {$topic}");
				$topics[$topic] = array("qos"=>0, "function"=>array($this, 'processMessage'));
			}
			if(!empty($topics)){
				$this->mqttClient->subscribe($topics,0);
				$stream = $this->mqttClient->getSocket();
				$this->registerStream($stream, 0);
				\Log::info("MQTT: subscribed");
			}
			
			$this->status = "connected";
			
			return true;
		}
		
		return false;
	}
	
	public function disconnect(){
		if($this->status !== "disconnected"){
			\Log::info("MQTT: disconnect");
			$this->mqttClient->close();
			$this->unregisterAll();
			$this->status = "disconnected";
			$this->device->setConnectState(false);
		}
	}
	
	public function getStatus(){
		return $this->status;
	}
	
	public function process($stream, $id){
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
				\Log::info("MQTT: disconnected by the host");
				
				$this->unregisterAll();
				$this->status = "disconnected";
				$this->device->setConnectState(false);
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
			\Log::debug("MQTT: publish to topic {$topic}");
			
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
	
}
