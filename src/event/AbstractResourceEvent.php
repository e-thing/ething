<?php

namespace Ething\Event;


use \Ething\ResourceQueryParser;

use \Ething\Ething;

abstract class AbstractResourceEvent extends Event {
	
	
	static public function validateResourceAttr(Ething $ething, $resourceFilter, array $onlyTypes = null){
		if(is_string($resourceFilter) && !empty($resourceFilter)){
			// can either be an id or an expression
			if(\Ething\ShortId::validate($resourceFilter)){
				$resource = $ething->get($resourceFilter);
				if(!$resource)
					throw new \Exception("the resource with id '{$resourceFilter}' does not exist.");
				if(!empty($onlyTypes)){
					
					$pass = false;
					foreach($onlyTypes as $type){
						if($resource->isTypeof($type)){
							$pass = true;
							break;
						}
					}
					
					if(!$pass)
						throw new \Exception("the resource with id '{$resourceFilter}' and type {$resource->type()} must be one of the following types : ".implode(', ',$onlyTypes));
				}
			}
			else {
				// parse the expression
				if(!ResourceQueryParser::check($ething, $resourceFilter, $error))
					throw new \Exception('invalid expression: '.$error);
			}
		}
		else if(is_array($resourceFilter) && !empty($resourceFilter)){
			// must be an array of ids
			
			foreach($resourceFilter as $id){
				if(\Ething\ShortId::validate($id)){
					$resource = $ething->get($id);
					if(!$resource)
						throw new \Exception("the resource with id '{$id}' does not exist.");
					if(!empty($onlyTypes)){
						
						$pass = false;
						foreach($onlyTypes as $type){
							if($resource->isTypeof($type)){
								$pass = true;
								break;
							}
						}
						
						if(!$pass)
							throw new \Exception("the resource with id '{$id}' and type {$resource->type()} must be one of the following types : ".implode(', ',$onlyTypes));
					}
				} else
					throw new \Exception("not a valid array of resource's id.");
			}
		}
		else if(isset($resourceFilter))
			throw new \Exception("invalid.");
	}
	
	static public function validate(array &$attributes, array $context){
		
		foreach($attributes as $key => &$value){
			
			switch($key){
				
				case 'resource': // optional (if not set, the event will be fired on every resource)
					
					try {
						$onlyTypes = null;
						if(!empty($context['onlyTypes'])){
							if(is_array($context['onlyTypes'])) $onlyTypes = $context['onlyTypes'];
							else if(is_string($context['onlyTypes'])) $onlyTypes = array($context['onlyTypes']);
						}
						static::validateResourceAttr($context['ething'], $value, $onlyTypes);
					} catch(\Exception $e){
						throw new \Exception("[{$key}] ".$e->getMessage(),$e->getCode(),$e);
					}
					
					break;
					
				default:
					
					if(isset($context['keyValidator']) && is_callable($context['keyValidator'])){
						if(call_user_func_array($context['keyValidator'], array($key, &$value, $context)) === false)
							throw new \Exception("invalid attribute '{$key}'.");
					} else {
						throw new \Exception("attribute '{$key}' unknown.");
					}
					
			}
			
		}
		
		return true; 
	}
	
	
	static public function filter(Ething $ething, $resourceIdFromSignal, $resourceFilter){
		if(!isset($resourceFilter)) { // no filtering
			return true;
		} else if(isset($resourceIdFromSignal)) {
			if( is_string($resourceFilter) ) {
			
				if(\Ething\ShortId::validate($resourceFilter)){ // resource id
					return $resourceFilter === $resourceIdFromSignal;
				}
				else { // query string
					// check if the resource from the signal match the expression
					return boolval( $ething->findOne( array(
						'$and' => array(
							array( '_id' => $resourceIdFromSignal ),
							$ething->resourceQueryParser()->parse($resourceFilter)
						)
					) ) );
				}
			} else if( is_array($resourceFilter) ) { // array of resource ids
				return in_array($resourceIdFromSignal, $resourceFilter);
			}
		}
		return false;
	}
	
	protected function call(Signal $signal){
		return static::filter($this->ething(), isset($signal->resource) ? $signal->resource : null, isset($this->resource) ? $this->resource : null);
	}
	
}

