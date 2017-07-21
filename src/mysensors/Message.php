<?php


namespace Ething\MySensors;

class Message implements \JsonSerializable {
	
	
	public $nodeId;
	public $childSensorId;
	public $messageType;
	public $ack;
	public $subType;
	public $payload;
	
	public function __construct($nodeId, $childSensorId, $messageType, $ack, $subType, $payload = ''){
		$this->nodeId = intval($nodeId);
		$this->childSensorId = intval($childSensorId);
		$this->messageType = intval($messageType);
		$this->ack = intval($ack);
		
		if(is_numeric($subType)){
			$this->subType = intval($subType);
		} else if(MySensors::isSensorTypeStr($subType)){
			$this->subType = MySensors::sensorTypeInt($subType);
		} else if(MySensors::isValueTypeStr($subType)){
			$this->subType = MySensors::valueTypeInt($subType);
		}
		
		$this->payload = is_bool($payload) ? ($payload ? '1' : '0') : strval($payload);
	}
	
	static public function parse($message){
		
		// remove newline char
		$message = preg_replace("/\r?\n$/","",$message);
		
		$parts = explode(';', $message);
		if(count($parts)===6){
			return new Message(
				intval($parts[0]),
				intval($parts[1]),
				intval($parts[2]),
				intval($parts[3]),
				intval($parts[4]),
				$parts[5]
			);
		} else {
			throw new Exception('invalid message');
		}
	}
	
	public function stringify(){
		return sprintf("%d;%d;%d;%d;%d;%s\n", $this->nodeId, $this->childSensorId, $this->messageType, $this->ack, $this->subType, $this->payload);
	}
	
	public function toHumanReadable(){
		$messageTypeStr = array_search($this->messageType, MySensors::$messageTypes);
		$subTypeStr = false;
		switch($this->messageType){
			case MySensors::PRESENTATION :
				$subTypeStr = array_search($this->subType, MySensors::$sensorTypes);
				break;
			case MySensors::SET :
			case MySensors::REQ :
				$subTypeStr = array_search($this->subType, MySensors::$valueTypes);
				break;
			case MySensors::INTERNAL :
				$subTypeStr = array_search($this->subType, MySensors::$internalTypes);
				break;
		}
		if(!$messageTypeStr) $messageTypeStr = (string)$this->messageType;
		if(!$subTypeStr) $subTypeStr = (string)$this->subType;
		
		return sprintf("%d;%d;%s;%d;%s;%s\n", $this->nodeId, $this->childSensorId, $messageTypeStr, $this->ack, $subTypeStr, $this->payload);
	}
	
	public function __toString(){
		return $this->stringify();
	}
	
	public function jsonSerialize() {
		return get_object_vars($this);
	}
	
	public function fromHex() {
		return \hex2bin($this->payload);
	}
	
	public function getValue() {
		switch($this->messageType){
			case MySensors::SET :
			case MySensors::REQ :
				
				switch($this->subType){
					// number
					case MySensors::V_TEMP :
					case MySensors::V_HUM :
					case MySensors::V_PERCENTAGE :
					case MySensors::V_PRESSURE :
					case MySensors::V_RAIN :
					case MySensors::V_RAINRATE :
					case MySensors::V_WIND :
					case MySensors::V_DIRECTION :
					case MySensors::V_UV :
					case MySensors::V_WEIGHT :
					case MySensors::V_DISTANCE :
					case MySensors::V_IMPEDANCE :
					case MySensors::V_WATT :
					case MySensors::V_KWH :
					case MySensors::V_LIGHT_LEVEL :
					case MySensors::V_FLOW :
					case MySensors::V_VOLUME :
					case MySensors::V_LEVEL :
					case MySensors::V_VOLTAGE :
					case MySensors::V_CURRENT :
					case MySensors::V_PH :
					case MySensors::V_ORP :
					case MySensors::V_EC :
					case MySensors::V_VAR :
					case MySensors::V_VA :
					case MySensors::V_POWER_FACTOR :
						if(is_numeric($this->payload))
							return $this->payload + 0;
					
					// bool
					case MySensors::V_STATUS :
					case MySensors::V_ARMED :
					case MySensors::V_TRIPPED :
					case MySensors::V_LOCK_STATUS :
						return $this->payload === '1';
						
				}
				
				return $this->payload;
				
			default :
				return $this->payload;
		}
	}
};


