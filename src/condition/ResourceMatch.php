<?php


namespace Ething\Condition;

use \Ething\ResourceQueryParser;
	
class ResourceMatch extends AbstractResourceCondition {
	
	
	static public function validate(array &$attributes, array $context){
		
		$attributes = array_merge(
			array( 
				'resource' => null,
				'expression' => null
			),
			$attributes
		);
		
		foreach($attributes as $key => &$value){
			
			switch($key){
				
				case 'resource':
					
					try {
						static::validateResourceAttr($context['ething'], $value);
					} catch(\Exception $e){
						throw new \Exception("[{$key}] ".$e->getMessage(),$e->getCode(),$e);
					}
					break;
				
				case 'expression':
					
					if(!is_string($value) || empty(trim($value)))
						throw new \Exception("field '{$key}' must be a non empty string.");
					
					// parse the query string
					if(!ResourceQueryParser::check($context['ething'], $value, $error))
						throw new \Exception('invalid expression: '.$error);
					
					break;
				
				default:
					throw new \Exception("field '{$key}' unknown.");
			}
			
		}
		
		return true; 
	}
	
	protected function call(\Ething\Event\Signal $signal){
		$resources = $this->getResources($signal);
		
		foreach($resources as $r){
			return $r->match($this->expression);
		}
	}
	
	
}


