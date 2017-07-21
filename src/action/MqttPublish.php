<?php


namespace Ething\Action;


use \Ething\MQTT\phpMQTT;

class MqttPublish extends Action {
	
	static public function validate(array &$attributes, array $context){
		
		$attributes = array_merge(
			array( 
				'host' => null,
				'port' => 1883,
				'topic' => null,
				'payload' => null,
				'username' => null,
				'password' => null
			),
			$attributes
		);
		
		foreach(array_keys($attributes) as $key){
			
			switch($key){
				
				case 'host':
				case 'topic':
				case 'payload':
					if(!is_string($attributes[$key]) || empty($attributes[$key]))
						throw new \Exception("field '{$key}' must be a non empty string.");
					break;
				
				case 'port':
					if(!is_int($attributes[$key]) || $attributes[$key]<0 || $attributes[$key]> 65535)
						throw new \Exception("field '{$key}' must be a valid port number (eg. 1883).");
					break;
				
				case 'username':
				case 'password':
					if(!(is_null($attributes[$key]) || (is_string($attributes[$key]) && empty($attributes[$key]))))
						throw new \Exception("field '{$key}' must be a non empty string or null.");
					break;
					
				default:
					throw new \Exception("field '{$key}' unknown.");
			}
			
		}
		
		return true; 
	}
	
	
	protected function call(\Ething\Event\Signal $signal){
		
		$mqttClient = new phpMQTT($this->host, $this->port, \uniqid());
		
		if($mqttClient->connect(true, NULL, $this->username, $this->password)){
			$mqttClient->publish($this->topic,$this->payload,0);
			$mqttClient->close();
		} else {
			throw new \Exception("MQTT: Unable to connect {$this->host}:{$this->port}");
		}
		
	}
	
}



