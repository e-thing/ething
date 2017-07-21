<?php

namespace Ething\Event;

use \Ething\Resource;

class Custom extends AbstractResourceEvent {
	
	
	static public function emit($name, Resource $resource = null){
		return new Signal('Custom', array(
			'name' => $name,
			'resource' => isset($resource) ? $resource->id() : null
		));
	}
	
	
	static public function validate(array &$attributes, array $context){
		
		$attributes = array_merge(
			array( 
				'name' => null,
				'resource' => null
			),
			$attributes
		);
		
		foreach(array_keys($attributes) as $key){
			
			switch($key){
				
				case 'name':
					if(!is_string($attributes[$key]) || empty($attributes[$key]))
						throw new \Exception("field '{$key}' must be a non empty string.");
					break;
				
				case 'resource':
					try {
						static::validateResourceAttr($context['ething'], $attributes[$key]);
					} catch(\Exception $e){
						throw new \Exception("[{$key}] ".$e->getMessage(),$e->getCode(),$e);
					}
					break;
					
				default:
					throw new \Exception("field '{$key}' unknown.");
			}
			
		}
		
		return true;
	}
	
	protected function call(Signal $signal){
		return $this->name === $signal->name && parent::call($signal);
	}
	
}
