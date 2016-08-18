<?php


namespace Ething\Condition;
	
class TableValueThreshold extends Condition {
	
	public $threshold;
	public $field;
	public $operator;
	
	
	static public function check(array &$json, $eventName, $resourceTypeName){
		
		if(!(isset($json['field']) && is_string($json['field']) && !empty($json['field'])))
			throw new \Ething\Exception('invalid value for the field "field"');
		if(!(isset($json['threshold']) && (is_int($json['threshold']) || is_float($json['threshold']))))
			throw new \Ething\Exception('invalid value for the field "threshold"');
		if(!(isset($json['operator']) && in_array($json['operator'],array('<','>','<=','>=','==','!='))))
			throw new \Ething\Exception('invalid value for the field "operator"');
		
		return $eventName == 'TableDataAdded' && $resourceTypeName == 'Table';
	}
	
	public function test(\Ething\Event\Event $event){
		
		$value = isset($event->value[$this->field]) ? $event->value[$this->field] : null;
		
		if (is_numeric($value)) {
			return eval("return {$value} {$this->operator} {$this->threshold};");
		}
		
		return false;
	}
	
	public function description(){
		$opStr = '?';
		switch($this->operator){
			case '>':
				$opStr = 'greater than';
				break;
			case '<':
				$opStr = 'lower than';
				break;
			case '>=':
				$opStr = 'greater or equal';
				break;
			case '<=':
				$opStr = 'less or equal';
				break;
			case '==':
				$opStr = 'equal';
				break;
			case '!=':
				$opStr = 'not equal';
				break;
		}
		return "the value of the field '{$this->field}' is {$opStr} {$this->threshold}";
	}
	
}


