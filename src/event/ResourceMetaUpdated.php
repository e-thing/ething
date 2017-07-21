<?php

namespace Ething\Event;

use \Ething\ResourceQueryParser;


class ResourceMetaUpdated extends AbstractResourceEvent {
	
	
	
	static public function emit(\Ething\Resource $resource, array $attributes){
		return new Signal('ResourceMetaUpdated', array(
			'resource' => $resource->id(), // the updated resource
			'resourceName' => $resource->name(),
			'attributes' => $attributes // list of names of the attributes that has been updated
		));
	}
	
	
	static public function validate(array &$attributes, array $context){
		
		$context['keyValidator'] = function($key, &$value,$context){
			
			switch($key){
				
				case 'attributes': // list of names of the attributes to listen to some update
					
					if(\Ething\Helpers::is_numeric_array($value)){
						foreach($value as $attr){
							if(!is_string($attr))
								throw new \Exception("the '{$key}' must be an array of string");
						}
					} else if(!is_null($value))
						throw new \Exception("the '{$key}' must be an array of string");
					
					break;
					
				case 'filter': // an expression to use as an extended filter
					
					if(is_string($value)){
						// parse the expression
						if(!ResourceQueryParser::check($context['ething'], $value, $error))
							throw new \Exception('invalid expression: '.$error);
					} else if(!is_null($value))
						throw new \Exception("the '{$key}' must be a string");
					
					break;
				
				default:
					return false;
			}
			
		};
		
		return parent::validate($attributes, $context);
	}
	
	protected function call(Signal $signal){
		if((!isset($this->attributes) || count(array_intersect($this->attributes, $signal->attributes))) && parent::call($signal)){
			return !isset($this->filter) || boolval( $this->ething()->findOne( array(
					'$and' => array(
						array( '_id' => $signal->resource ),
						$this->ething()->resourceQueryParser()->parse($this->filter)
					)
				) ) );
		}
		return false;
	}
	
}

