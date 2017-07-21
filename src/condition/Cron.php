<?php


namespace Ething\Condition;


	
class Cron extends Condition {
	
	
	static public function validate(array &$attributes, array $context){
		
		$attributes = array_merge(
			array( 
				'cron' => null
			),
			$attributes
		);
		
		foreach(array_keys($attributes) as $key){
			
			switch($key){
				
				case 'cron':
					
					if(!is_string($attributes[$key]))
						throw new \Exception("field '{$key}' must be a string.");
					
					if(empty($attributes[$key]) || !\Cron\CronExpression::isValidExpression($attributes[$key]))
						throw new \Ething\Exception('invalid cron expression');
					
					break;
				
				default:
					throw new \Exception("field '{$key}' unknown.");
			}
			
		}
		
		return true; 
	}
	
	protected function call(\Ething\Event\Signal $signal){
		$cron = \Cron\CronExpression::factory($this->cron);
		return $cron->isDue();
	}
	
}


