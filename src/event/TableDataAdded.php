<?php

namespace Ething\Event;

class TableDataAdded extends AbstractResourceEvent {
	
	static public function emit(\Ething\Table $resource, \stdClass $data){
		return new Signal('TableDataAdded', array(
			'resource' => $resource->id(),
			'resourceName' => $resource->name(),
			'data' => $data
		));
	}
	
	
	static public function validate(array &$attributes, array $context){
		
		$attributes = array_merge(
			array( 
				'resource' => null,
				'filter' => null
			),
			$attributes
		);
		
		foreach($attributes as $key => &$value){
			
			switch($key){
				
				case 'resource':
					try {
						static::validateResourceAttr($context['ething'], $value, array('Table'));
					} catch(\Exception $e){
						throw new \Exception("[{$key}] ".$e->getMessage(),$e->getCode(),$e);
					}
					break;
				
				case 'filter': // an expression to filter according to the values
					
					if(is_string($value)){
						// parse the expression
						if(!TableQueryParser::check($value, $error))
							throw new \Exception('invalid expression: '.$error);
					} else if(!is_null($value))
						throw new \Exception("the '{$key}' must be a string");
					
					break;
					
				default:
					throw new \Exception("attribute '{$key}' unknown.");
					
			}
			
		}
		
		return true; 
	}
	
	
	protected function call(Signal $signal){
		
		if(parent::call($signal)){
			
			if(isset($this->filter)){
				
				$table = $signal->resource;
					
				return boolval( count( $table->select(null,1,null,null,array(
					'$and' => array(
						array( '_id' => $this->data->id ),
						$table->parser()->parse($this->filter)
					)
				) )  ) );
				
			} else return true;
			
		}
		
		return false;
	}
	
	
}
