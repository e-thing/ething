<?php

namespace Ething\Action;


use \Ething\Ething;
use \Ething\ResourceQueryParser;
use \Ething\Event\Signal;
use \Ething\InvalidRuleException;

abstract class AbstractResourceAction extends Action {
	
	
	static public function validateResourceAttr(Ething $ething, $resourceFilter, array $onlyTypes = null){
		if(is_string($resourceFilter) && !empty($resourceFilter)){
			// can either be an id or an expression or a special keywords
			if($resourceFilter==='#emitter'){
				
			}
			else if(\Ething\ShortId::validate($resourceFilter)){
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
						throw new \Exception("the resource with id '{$resourceFilter}' must be one of the following types : ".implode(', ',$onlyTypes));
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
	
	static public function getResourcesStatic(Ething $ething, $resource, Signal $signal = null){
		$rs = array();
		
		if( is_string($resource) ) {
			
			if($resource==='#emitter'){
				if(isset($signal->resource)){
					$r = $ething->get($signal->resource);
					if(!$r)
						throw new \Exception("unable to find the resource with id '{$signal->resource}'");
					$rs[] = $r;
				} else {
					throw new \Exception('this signal was not emitted by a resource');
				}
			}
			else if(\Ething\ShortId::validate($resource)){
				$r = $ething->get($resource);
				if(!$r)
					throw new InvalidRuleException("unable to find the resource with id '{$resource}'");
				$rs[] = $r;
			}
			else {
				// expression
				$rs = $ething->find($resource);
			}
		} else if( is_array($resource) ) {
			
			$notFound = array();
			foreach($resource as $id){
				$r = $ething->get($id);
				if(!$r)
					$notFound[] = $id;
				$rs[] = $r;
			}
			
			if(!empty($notFound)){
				if(count($notFound) === count($resource))
					throw new InvalidRuleException("unable to find the resources with id :".implode(',',$notFound));
				else
					throw new \Exception("unable to find the resources with id :".implode(',',$notFound));
			}
		}
		
		return $rs;
	}
	
	protected function getResources(Signal $signal, $resource = null){
		return static::getResourcesStatic($this->ething(), isset($resource) ? $resource : $this->resource, $signal);
	}
	
}

