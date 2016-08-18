<?php

namespace Ething\Action;


interface ActionInterface {
	static public function check(array &$json, $eventName, $resourceTypeName);
}
	
	
abstract class Action implements \JsonSerializable, ActionInterface {
	
	public $type;
	
	abstract public function execute(\Ething\Event\Event $event, \Rule $rule);
	
	
	public function __construct(array $json){
		// set the property's value of this instance
		foreach($json as $attr => $value)
			$this->$attr = $value;
		$this->type = get_class($this);
	}
	
	public function jsonSerialize(){
		return get_object_vars($this);
	}
	
	// default : compatible with all events
	static public function check(array &$json, $eventName, $resourceTypeName){
		return true;
	}
}





