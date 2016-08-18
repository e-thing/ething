<?php


namespace Ething\Condition;
	
class DeviceBatteryLevel extends Condition {
	
	public $threshold;
	public $operator;
	
	static public function check(array &$json, $eventName, $resourceTypeName){
		
		if(!(isset($json['threshold']) && (is_int($json['threshold']) || is_float($json['threshold'])) && $json['threshold'] <= 100 && $json['threshold'] >= 0))
			throw new \Ething\Exception('invalid value for the field "threshold"');
		if(!(isset($json['operator']) && in_array($json['operator'],array('<','>','<=','>=','==','!='))))
			throw new \Ething\Exception('invalid value for the field "operator"');
		
		return $resourceTypeName == 'Device';
	}
	
	public function test(\Ething\Event\Event $event){
		$device = $event->target();
		$battery = $device->battery();
		return is_numeric($battery) && eval("return {$battery} {$this->operator} {$this->threshold};");
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
		return "the device has a battery level {$opStr} {$this->threshold}%";
	}
	
}


