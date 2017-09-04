<?php

namespace Ething;


/**
 * @swagger-definition
 * "Rule":{ 
 *   "type": "object",
 *   "description": "

A rule object. A rule is consisted of three parts:

- The event part specifies the signal that triggers the invocation of the rule
- The condition part is a logical test that, if satisfied, causes the action to be carried out
- The action part

",
 *   "required":["events", "actions"],
 * 	 "properties":{
 * 		"events":{  
 * 		   "type":"array",
 * 		   "items":{
 * 		      "$ref": "#/definitions/Event"
 * 		   },
 * 		   "description":"A collection of events. The rule will be executed each time an event from the collection is dispatched."
 * 		},
 * 		"conditions":{  
 * 		   "type":"array",
 * 		   "items":{
 * 		      "$ref": "#/definitions/Condition"
 * 		   },
 * 		   "description":"A collection of conditions. May be empty."
 * 		},
 * 		"actions":{
 * 		   "type":"array",
 * 		   "items":{
 * 		      "$ref": "#/definitions/Action"
 * 		   },
 * 		   "description":"A collection of actions. Must not be empty !"
 * 		},
 * 		"executedDate":{  
 * 		   "type":"string",
 * 		   "format":"date-time",
 * 		   "description":"The last time this rule has been executed.",
 *         "readOnly": true
 * 		},
 * 		"executedCount":{  
 * 		   "type":"integer",
 * 		   "description":"The number of time this rule has been executed.",
 *         "readOnly": true
 * 		},
 * 		"createdDate":{  
 * 		   "type":"string",
 * 		   "format":"date-time",
 * 		   "description":"The time this rule was created.",
 *         "readOnly": true
 * 		},
 * 		"state":{  
 * 		   "type":"string",
 * 		   "description":"The state of this rule.",
 *         "readOnly": true,
 *         "enum": ["active", "inactive", "invalid"]
 * 		},
 * 		"enabled":{  
 * 		   "type":"boolean",
 * 		   "description":"If this rule is enabled or not."
 * 		},
 * 		"name":{  
 * 		   "type":"string",
 * 		   "description":"The name of this rule. Two or more rules can share the same name."
 * 		},
 * 		"priority":{  
 * 		   "type":"integer",
 * 		   "description":"The priority of this rule. Rules with highest priority will be executed first."
 * 		},
 * 		"repeat":{  
 * 		   "type":"boolean",
 * 		   "description":"If repeat is set to false, the actions of this rule will be executed only the first time the conditions match. Default to true."
 * 		}
 * 	 }
 * }
 */

 
/**
 * @swagger-definition
 * "Event":{ 
 *   "type": "object",
 *   "description": "
The base representation of an event object used in rule.

For exemple, a rule that will be running every hour will have the following event :

```json
{
  \"type\": \"Timer\",
  \"cron\" : \"0 * * * *\"
}
```

",
 *   "required":["type"],
 * 	 "properties":{
 * 		"type":{  
 * 		   "type":"string",
 * 		   "description":"The type of the event."
 * 		}
 * 	 }
 * }
 */
 
/**
 * @swagger-definition
 * "Condition":{ 
 *   "type": "object",
 *   "description": "
The base representation of a condition object used in rule.
",
 *   "required":["type"],
 * 	 "properties":{
 * 		"type":{  
 * 		   "type":"string",
 * 		   "description":"The type of the condition."
 * 		},
 * 		"isInvalid":{  
 * 		   "type":"boolean",
 * 		   "description":"Set to true if this condition is invalid.",
 * 		   "readOnly": true
 * 		}
 * 	 }
 * }
 */
 
/**
 * @swagger-definition
 * "Action":{ 
 *   "type": "object",
 *   "description": "
The base representation of an action object used in rule.
",
 *   "required":["type"],
 * 	 "properties":{
 * 		"type":{  
 * 		   "type":"string",
 * 		   "description":"The type of the action."
 * 		},
 * 		"isInvalid":{  
 * 		   "type":"boolean",
 * 		   "description":"Set to true if this action is invalid.",
 * 		   "readOnly": true
 * 		}
 * 	 }
 * }
 */

use \Ething\Helpers;
use \Ething\Event\Signal;
use \Ething\Event\Event;
use \Ething\Condition\Condition;
use \Ething\Action\Action;
 
class Rule implements \JsonSerializable {
	
	private $_d;
	
	private $_events = null;
	private $_conditions = null;
	private $_actions = null;
	
	private $_ething;
	
	
	// before calling this function, call validate(...) to check if the data are valid or not !
	public function __construct(Ething $ething, array $data)
	{
		$this->_ething = $ething;
		$this->_d = $data;
	}
	
	public function id() {
		return $this->_d['_id'];
    }
	
	public function ething() {
		return $this->_ething;
    }
	
	protected function events(){
		if($this->_events === null){
			$this->_events = array();
			foreach($this->_d['events'] as &$event){
				$classname = 'Ething\\Event\\'.$event['type'];
				if(class_exists($classname)) {
					$this->_events[] = new $classname($this, $event);
				} else {
					throw new Exception("Event '{$classname}' unknown");
				}
			}
		}
		return $this->_events;
	}
	
	protected function conditions(){
		if($this->_conditions === null){
			$this->_conditions = array();
			foreach($this->_d['conditions'] as &$condition){
				$classname = 'Ething\\Condition\\'.$condition['type'];
				if(class_exists($classname)) {
					$this->_conditions[] = new $classname($this, $condition);
				} else {
					throw new Exception("Condition '{$classname}' unknown");
				}
			}
		}
		return $this->_conditions;
	}
	
	protected function actions(){
		if($this->_actions === null){
			$this->_actions = array();
			foreach($this->_d['actions'] as &$action){
				$classname = 'Ething\\Action\\'.$action['type'];
				if(class_exists($classname)) {
					$this->_actions[] = new $classname($this, $action);
				} else {
					throw new Exception("Action '{$classname}' unknown");
				}
			}
		}
		return $this->_actions;
	}
	
	
	public function __get($name)
    {
		return isset($this->_d[$name]) ? $this->_d[$name] : null;
    }
	
	
	protected function evaluate(Signal $signal){
		
		$pass = true;
		
		// tests the conditions
		foreach($this->conditions() as $condition){
			
			$test = $condition->evaluate($signal);
			
			if($condition->isDirty()){
				$this->update();
			}
			
			$this->_ething->logger()->debug("rule {$this->id()} '{$this->name}' evaluate condition '{$condition->getType()}' result:{$test}");
			
			if(!$test){
				$pass = false;
				break;
			}
		}
		
		return $pass;
	}
	
	protected function execute(Signal $signal){
		
		$this->_d['executedDate'] = new \MongoDB\BSON\UTCDateTime();
		$this->_d['executedCount']++;
		$this->update();
		
		// execute the actions
		foreach($this->actions() as $action){
			
			if($signal->isPropagationStopped()){
				$this->_ething->logger()->debug("rule {$this->id()} '{$this->name}' signal propagation stopped");
				break;
			}
			
			$this->_ething->logger()->debug("rule {$this->id()} '{$this->name}' executing action '{$action->getType()}'");
			
			$action->execute($signal);
			
			if($action->isDirty()){
				$this->update();
			}
		}
		
	}
	
	protected function run(Signal $signal = null){
		if(!isset($signal)) $signal = new Signal('manual');
		
		$executed = false;
		$evaluated = $this->evaluate($signal);
		
		$lastEval = !empty($this->_d['_lastEval']);
		$repeat = !empty($this->_d['repeat']);
		$this->_d['_lastEval'] = $evaluated;
		
		$this->_ething->logger()->debug("rule {$this->id()} '{$this->name}' eval:{$evaluated} lastEval:{$lastEval} repeat:{$repeat}");
		
		if(!$repeat && $lastEval)
			$evaluated = false;
		
		if($evaluated){
			$executed = true;
			$this->execute($signal);
		} else {
			$this->update();
		}
		
		return $executed;
	}
	
	
	public function jsonSerialize(){
		return Ething::r_encode($this->_d);
	}
	
	
	public static function validate(Ething $ething, array &$attr){
		
		$context = array(
			'ething' => $ething
		);
		
		$validate_item = function ($kind, &$data) use ($context) {
			
			if(is_object($data))
				$data = (array)$data; // cast object into associative array
			
			if(!is_array($data))
				throw new Exception("[Rule.{$kind}] Must be an object.");
			
			$data = array_merge(array(
				'type' => null,
				'options' => array()
			),$data);
			
			foreach(array_keys($data) as $key){
				switch($key){
					case 'type':
						if(!is_string($data[$key]))
							throw new Exception("[Rule.{$kind}.type] must be a string.");
						break;
					case 'options':
						if(is_null($data[$key]))
							$data[$key] = array();
						if(is_object($data[$key]))
							$data[$key] = (array)$data[$key];
						if(!Helpers::is_assoc($data[$key]))
							throw new Exception("[Rule.{$kind}.options] must be an object.");
						break;
					default:
						throw new Exception("[Rule.{$kind}] Unknown field '{$key}'.");
				}
			}
			
			
			$type = $data['type'];
			$attr = &$data['options'];
			
			if(empty($data['type']))
				throw new Exception("[Rule.{$kind}] No 'type' field.");
			
			$class = 'Ething\\'.ucfirst($kind).'\\'.$type;
			
			if(!class_exists($class)){
				throw new Exception("[Rule] Unknown {$kind} '{$type}'");
			}
			
			
			try {
				if(!call_user_func_array(array($class, 'validate'),array(&$attr,$context))){
					throw new \Exception("Invalid atributes.");
				}
			}
			catch(\Exception $e){
				throw $e;
				//throw new \Exception("[Rule.{$kind}] ".$e->getMessage(), 0, $e);
			}
			
			$data = array_merge(array(
				'error' => false,
				'isInvalid' => false
			),$data);
			
		};
		
		
		foreach(array_keys($attr) as $key){
			switch($key){
				case 'name':
					if(!is_string($attr[$key]))
						throw new Exception("[Rule] Invalid field '{$key}'. Must be a string.");
					break;
				case 'enabled':
				case 'repeat':
					if(!is_bool($attr[$key]))
						throw new Exception("[Rule] Invalid field '{$key}'. Must be a boolean.");
					break;
				case 'priority':
					if(!is_int($attr[$key]))
						throw new Exception("[Rule] Invalid field '{$key}'. Must be an integer.");
					break;
				case 'actions':
				case 'events':
					if(is_array($attr[$key]) && count($attr[$key])===0)
						throw new Exception("[Rule] no '{$key}'.");
				case 'conditions':
					if(!is_array($attr[$key]))
						throw new Exception("[Rule] Invalid field '{$key}'. Must be an array.");
					
					foreach($attr[$key] as &$item){
						$validate_item(substr($key, 0, -1), $item);
					}
					
					break;
				default:
					throw new Exception("[Rule] Unknown field '{$key}'.");
			}
		}
		
		return true;
	}
	
	public static function create(Ething $ething, array $attr){
		
		$attr = array_merge(array(
			'name' => "",
			'priority' => 0,
			'repeat' => true,
			'events' => array(),
			'conditions' => array(),
			'actions' => array()
		),$attr);
		
		self::validate($ething, $attr);
		
		if(empty($attr['actions']))
			throw new Exception("No actions set for that rule");
		
		$c = $ething->db()->selectCollection("rules");
		
		$data = array_merge($attr,array(
			'_id' => ShortId::generate(),
			'createdDate' => new \MongoDB\BSON\UTCDateTime(),
			'executedDate' => null,
			'executedCount' => 0,
			'enabled' => true
		));
		
		try {
			$c->insertOne($data);
		}
		catch(\MongoDB\Exception\Exception $e) {
			throw new Exception('db error: '.$e->getMessage());
		}
		
		$rule = new Rule($ething, $data);
		
		return $rule;
	}
	
	
	public function remove() {
		$c = $this->_ething->db()->selectCollection("rules");
		
		$c->deleteOne(array('_id' => $this->id()));
		
		$this->_d = null;
		$this->_conditions = null;
		$this->_actions = null;
	}
	
	public function set(array $attr) {
		
		self::validate($this->_ething, $attr);
		
		$attr = array_merge($this->_d, $attr);
		
		if(empty($attr['actions']))
			throw new Exception("No actions set for that rule");
		
		$this->_d = $attr;
		
		$this->update();
		
		$this->_conditions = null;
		$this->_actions = null;
		
		return true;
	}
	
	public function update(){
		$c = $this->_ething->db()->selectCollection("rules");
		$c->replaceOne(array('_id' => $this->id()), $this->_d);
	}
	
	
	public function trigger(Signal $signal){
		if($this->enabled){
			foreach($this->events() as $event){
				if($signal->getName() === $event->getType()){
					
					$pass = false;
					try {
						$pass = $event->match($signal);
					} catch (\Exception $e){
						$this->_ething->logger()->error($e);
					}
					
					if($pass){
						$this->run($signal);
						return true;
					}
				}
			}
		}
		return false;
	}
	
	
}





