<?php


namespace Ething\Condition;


interface ConditionInterface {
	static public function check(array &$json, $eventName, $resourceTypeName);
}

abstract class Condition implements \JsonSerializable, ConditionInterface {
	
	public $type;
	
	abstract public function test(\Ething\Event\Event $event);
	
	public function description(){
		return "the ".get_class()." condition matches";
	}
	
	public function __construct(array $json){
		// set the property's value of this instance
		foreach($json as $attr => $value)
			$this->$attr = $value;
		$this->type = get_class($this);
	}
	
	public function jsonSerialize(){
		return get_object_vars($this);
	}
	
	
}


	

