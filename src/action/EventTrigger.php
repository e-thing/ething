<?php


namespace Ething\Action;
	
class EventTrigger extends Action {
	
	
	// attributes validation function
	static public function validate(array &$attributes, array $context){
		
		$attributes = array_merge(
			array( 'name' => null ),
			$attributes
		);
		
		foreach(array_keys($attributes) as $key){
			
			switch($key){
				
				case 'name':
				
					if(!is_string($attributes[$key]) || empty($attributes[$key]))
						throw new \Exception("field '{$key}' must be a non empty string.");
					
					break;
				
				default:
					throw new \Exception("field '{$key}' unknown.");
			}
			
		}
		
		return true; 
	}
	
	
	protected function call(\Ething\Event\Signal $signal){
		$this->ething()->dispatchSignal( Ething\Event\Custom::emit($this->name) );
	}
	
}


