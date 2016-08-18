<?php


namespace Ething\Action;
	
class ResourceRemove extends Action {
	
	// this action is compatible with all events
	static public function check(array &$json, $eventName, $resourceTypeName){
		return true;
	}
	
	public function execute(\Ething\Event\Event $event, \Ething\Rule $rule){
		$target = $event->target();
		$target->remove();
	}
	
}


