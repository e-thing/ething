<?php


namespace Ething\Action;
	
class Sleep extends Action {
	
	
	// attributes validation function
	static public function validate(array &$attributes, array $context){
		
		$attributes = array_merge(
			array( 'duration' => null ),
			$attributes
		);
		
		foreach(array_keys($attributes) as $key){
			
			switch($key){
				
				case 'duration':
				
					if(!is_int($attributes[$key]) || $attributes[$key]<1 || $attributes[$key]>3600)
						throw new \Exception("field '{$key}' must be an intger greater than 1 and lower than .");
					
					break;
				
				default:
					throw new \Exception("field '{$key}' unknown.");
			}
			
		}
		
		return true; 
	}
	
	
	protected function call(\Ething\Event\Signal $signal){
		\sleep($this->duration);
	}
	
}


