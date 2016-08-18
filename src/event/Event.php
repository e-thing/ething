<?php

namespace Ething\Event;


interface EventInterface {
	static public function check($resourceTypeName);
}

abstract class Event implements EventInterface {
	
	private $target = null;
	
	public function __construct(\Ething\Resource $target, array $customData = array())
	{
		foreach($customData as $key => $value){
			$this->$key = $value;
		}
		
		$this->target = $target;
		$this->timeStamp = time();
		$this->type = substr(get_class($this),13); // remove Ething\Event\
	}
	
	public function target(){
		return $this->target;
	}
	
	// must be implemented in the derived class !
	public function description(){
		return "the event ".get_class()." was emitted";
	}
	
	// default
	static public function check($resourceTypeName){
		return true;
	}
	
}


