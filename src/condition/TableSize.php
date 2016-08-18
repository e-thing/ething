<?php


namespace Ething\Condition;
	
class FileSize extends Condition {
	
	public $threshold;
	public $operator;
	
	static public function check(array &$json, $eventName, $resourceTypeName){
		
		if(!(isset($json['threshold']) && is_int($json['threshold'])))
			throw new \Ething\Exception('invalid value for the field "threshold"');
		if(!(isset($json['operator']) && in_array($json['operator'],array('<','>','<=','>=','==','!='))))
			throw new \Ething\Exception('invalid value for the field "operator"');
		
		return $resourceTypeName == 'File';
	}
	
	public function test(\Ething\Event\Event $event){
		$file = $event->target();
		return eval("return {$file->size()} {$this->operator} {$this->threshold};");
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
		return "the size of the file is {$opStr} {$this->threshold}";
	}
	
}


