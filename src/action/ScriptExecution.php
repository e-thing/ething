<?php


namespace Ething\Action;

	
class ScriptExecution extends Action {
	
	
	// attributes validation function
	static public function validate(array &$attributes, array $context){
		
		$attributes = array_merge(
			array( 'script' => null, 'arguments' => null ),
			$attributes
		);
		
		foreach(array_keys($attributes) as $key){
			
			switch($key){
				
				case 'script':
					
					$scriptId = $attributes[$key];
					
					if(\Ething\ShortId::validate($scriptId)){
						$resource = $ething->get($resourceFilter);
						if(!$resource)
							throw new \Exception("the resource with id '{$scriptId}' does not exist.");
						
						if(!($resource->isTypeof('File') && $resource->mime === 'application/javascript')){
							throw new \Exception("the resource with id '{$scriptId}' is not a script.");
						}
						
					} else throw new \Exception("field '{$key}' must be a script id.");
					
					break;
				
				case 'arguments':
					
					if(!(is_string($attributes[$key]) || is_null($attributes[$key])))
						throw new \Exception("field '{$key}' must be a string or set to null.");
					
					break;
				
				default:
					throw new \Exception("field '{$key}' unknown.");
			}
			
		}
		
		return true; 
	}
	
	
	protected function call(\Ething\Event\Signal $signal){
		
		$scriptResource = $this->ething()->get($this->script);
		if(!$scriptResource)
			throw new InvalidRuleException("unable to find the script with id '{$scriptResource}'");
		
		$res = \Ething\ScriptEngine::runFromFile($scriptResource, $this->arguments);
		
		if(!$res){
			throw new \Utils\Exception('Unable to execute the script');
		}
		
		if(!$res['ok']){
			throw new \Utils\Exception('Script error');
		}
		
	}
	
}


