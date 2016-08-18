<?php


namespace Ething\Action;
	
class ResourceClear extends Action {
	
	// this action is compatible with all events
	static public function check(array &$json, $eventName, $resourceTypeName){
		return $resourceTypeName == 'Table' || $resourceTypeName == 'File';
	}
	
	public function execute(\Ething\Event\Event $event, \Ething\Rule $rule){
		$target = $event->target();
		
		if($target instanceof \Ething\Table)
			$target->clear();
		else if($target instanceof \Ething\File)
			$target->write(null);
		else
			throw new \Exception('ResourceClear: unknown target type');
	}
	
}


