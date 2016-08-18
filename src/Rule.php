<?php

namespace Ething;



class Rule implements \JsonSerializable {
	
	private $_d;
	private $_conditions;
	private $_actions;
	private $_parent;
	
	// before calling this function, call check(...) to check if the data are valid or not !
	public function __construct(array &$data, Resource $parent)
	{
		$this->_d = &$data;
		$this->_conditions = array();
		$this->_actions = array();
		$this->_parent = $parent;
		
		foreach($data['conditions'] as $condition){
			$classname = 'Ething\\Condition\\'.$condition['type'];
			if(class_exists($classname)) {
				$this->_conditions[] = new $classname($condition);
			} else {
				throw new \Ething\Exception("Condition '{$classname}' unknown");
			}
		}
		
		foreach($data['actions'] as $action){
			$classname = 'Ething\\Action\\'.$action['type'];
			if(class_exists($classname)) {
				$this->_actions[] = new $classname($action);
			} else {
				throw new \Ething\Exception("Action '{$classname}' unknown");
			}
		}
	}
	
	public function parent(){
		return $this->_parent;
	}
	
	public function eventName(){
		return $this->_d['event'];
	}
	
	public function repeat(){
		return $this->_d['repeat'];
	}
	
	public function conditions(){
		return $this->_conditions;
	}
	
	public function actions(){
		return $this->_actions;
	}
	
	public function data(){
		return $this->_d;
	}
	
	public function executedDate(){
		return isset($this->_d['executedDate']) ? $this->_d['executedDate']->sec : null;
	}
	
	
	
	public static function check(array &$json, Resource $resource){
		
		$json = array_merge(array(
			'event' => null,
			'conditions' => array(),
			'actions' => array(),
			'repeat' => false,
			'executedDate' => null
		),(array)$json);
		
		if(!(is_string($json['event']) && !empty($json['event'])))
			throw new Exception("[Rule] Invalid field 'event'");
		
		if(!is_array($json['conditions']))
			throw new Exception("[Rule] Invalid field 'conditions'");
		
		if(!is_array($json['actions']))
			throw new Exception("[Rule] Invalid field 'actions'");
		
		if(!is_bool($json['repeat']))
			throw new Exception("[Rule] Invalid field 'repeat'");
		
		if(empty($json['actions']))
			throw new Exception("No action for that rule");
		
		$eventName = $json['event'];
		$eventClass = 'Ething\\Event\\'.$eventName;
		$resourceTypeName = preg_replace('/^Ething\\\/','',get_class($resource));
		
		if(!class_exists($eventClass)){
			throw new Exception("Unknown event '{$eventName}'");
		}
		
		if(!call_user_func(array($eventClass, 'check'),$resourceTypeName)){
			throw new Exception("The event '{$eventName}' is incompatible with this resource");
		}
		
		
		$i=0;
		foreach($json['conditions'] as &$condition){
			if(!(self::checkConditionOrAction('Condition', $condition, $eventName, $resourceTypeName)))
				throw new Exception("invalid or incompatible condition #{$i}");
			$i++;
		}
		
		$i=0;
		foreach($json['actions'] as &$action){
			if(!(self::checkConditionOrAction('Action', $action, $eventName, $resourceTypeName)))
				throw new Exception("invalid or incompatible action #{$i}");
			$i++;
		}
		
		return true;
	}
	
	private static function checkConditionOrAction($type, array &$json, $eventName, $resourceTypeName){
		if(!isset($json['type']))
			return false;
		
		$classname = 'Ething\\'.$type.'\\'.$json['type'];
		
		if (
			class_exists($classname) && 
			is_subclass_of($classname,'Ething\\'.$type.'\\'.$type.'')
		) {
			
			// only attributes that are defined in the class as public are allowed
			if(
				!array_reduce(array_keys($json),function($carry,$prop) use ($classname){
					return $carry && property_exists($classname,$prop);
				},true)
			) 
				return false;
			
			return call_user_func(array($classname, 'check'),$json,$eventName,$resourceTypeName);
		} else {
			throw new \Ething\Exception($type." '{$classname}' unknown");
		}
	}
	
	
	public function execute(Event\Event $event, &$errors = null){
		$errors = array();
		
		// check if this rule match with this event
		if( get_class($event) !== 'Ething\\Event\\'.$this->eventName() )
			return false;
		
		
		$pass = true;
		$executed = false;
		// tests the conditions
		try {
			foreach($this->_conditions as $condition)
				if(!$condition->test($event)){
					$pass = false;
					break;
				}
		}
		catch(\Exception $e){
			$pass = false;
			$errors[] = $e;
		}
		
		$lastPassState = isset($this->_d['_pass']) ? $this->_d['_pass'] : false;
		
		if($pass && ($this->repeat() || $lastPassState == false)){
			
			$executed = true;
			$this->_d['executedDate'] = new \MongoDate();
			
			// execute the actions
			foreach($this->_actions as $action){
				try {
					$action->execute($event, $this);
				}
				catch(\Exception $e){
					$errors[] = $e;
				}
			}
		}
		
		// save the data
		$this->_d['_pass'] = $pass;// save the pass state (used for the repeat feature)
		$this->parent()->update();
		
		return $executed;
	}
	
	public function jsonSerialize(){
		$lastExeTs = $this->executedDate();
		return array(
			'event' => $this->eventName(),
			'repeat' => $this->repeat(),
			'conditions' => $this->conditions(),
			'actions' => $this->actions(),
			'executedDate' => isset($lastExeTs) ? date(\DateTime::RFC3339, $lastExeTs) : null
		);
	}
	
	
	
	
}





