<?php


namespace Ething\Condition;
	
class TableLength extends Condition {
	
	public $threshold;
	public $operator;
	
	static public function check(array &$json, $eventName, $resourceTypeName){
		
		if(!(isset($json['threshold']) && is_int($json['threshold'])))
			throw new \Ething\Exception('invalid value for the field "threshold"');
		if(!(isset($json['operator']) && in_array($json['operator'],array('<','>','<=','>=','==','!='))))
			throw new \Ething\Exception('invalid value for the field "operator"');
		
		return $resourceTypeName == 'Table';
	}
	
	public function test(\Ething\Event\Event $event){
		$table = $event->target();
		
		return eval("return {$table->length()} {$this->operator} {$this->threshold};");
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
		return "the table rows number is {$opStr} {$this->threshold}";
	}
	
}


