<?php


namespace Ething\Condition;


	
class Cron extends Condition {
	
	public $cron;
	
	
	static public function check(array &$json, $eventName, $resourceTypeName){
		if(!(isset($json['cron']) && is_string($json['cron']) && !empty($json['cron']) && \Cron\CronExpression::isValidExpression($json['cron'])))
			throw new \Ething\Exception('invalid cron expression');
		
		return true;
	}
	
	public function test(\Ething\Event\Event $event){
		$cron = \Cron\CronExpression::factory($this->cron);
		return $cron->isDue();
	}
	
	public function description(){
		return "the current time matches the cron expression '{$this->cron}'";
	}
	
}


