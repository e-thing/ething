<?php


namespace Ething\Action;

use \Ething\Helpers;
	
class Log extends Action {
	
	
	// attributes validation function
	static public function validate(array &$attributes, array $context){
		
		$attributes = array_merge(
			array( 'message' => null ),
			$attributes
		);
		
		foreach(array_keys($attributes) as $key){
			
			switch($key){
				
				case 'message':
				
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
		$self = $this;
		
		$message = Helpers::percent_replace($this->message, function($tag) use ($signal, $self) {
			switch($tag){
				case '%%':
					return '%';
				case '%D':
					return date("Y-m-d H:i:s", $signal->getTimestamp());
				case '%R':
					if(isset($signal->resource)){
						if($r = $self->ething()->get($signal->resource))
							return $r->name();
					}
					break;
				case '%r':
					return $self->rule()->name;
					break;
				case '%s':
					return $signal->getName();
					break;
			}
		});
		
		$this->ething()->log($message, 'Action::Log');
	}
	
}


