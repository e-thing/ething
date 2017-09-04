<?php


namespace Ething\Action;


use \Ething\Device\Device;
use \Ething\StreamBuffer;
use \Ething\Helpers;

class DeviceRequest extends Action {
	
	static public function validate(array &$attributes, array $context){
		
		$attributes = array_merge(
			array( 
				'device' => null, // device id
				'operation' => null, // operation id
				'parameters' => null,
				'output' => null
			),
			$attributes
		);
		
		$device = null;
		
		foreach(array_keys($attributes) as $key){
			
			switch($key){
				
				case 'device':
					
					if(!is_string($attributes[$key]))
						throw new \Exception("field '{$key}' must be a string.");
					
					$device = $context['ething']->get($attributes[$key]);
					if(!$device || !($device instanceof Device))
						throw new \Exception("the resource with id '{$attributes[$key]}' does not exist or is not a Device.");
					
					break;
				
				case 'operation':
					
					if(empty($attributes[$key]) ||  !is_string($attributes[$key]))
						throw new \Exception("field '{$key}' must be a non empty string.");
					
					break;
					
				case 'parameters':
					
					if(is_object($attributes[$key]))
						$attributes[$key] = (array)$attributes[$key];
					
					if(!is_array($attributes[$key]) && ! is_null($attributes[$key]))
						throw new \Exception("field '{$key}' is invalid.");
					
					break;
				
				case 'output':
					
					$value = &$attributes[$key];
					
					if(is_object($value))
						$value = (array)$value;
					
					if(is_array($value) && is_string($value['type'])){
						
						$o = array(
							'type' => $value['type'],
							'expireAfter' => null
						);
						
						switch($value['type']){
							case 'file':
							case 'table':
								
								if(empty($value['name']) || !is_string($value['name']))
									throw new \Exception("field '{$key}.name' must be a non empty string.");
								
								$o['name'] = $value['name'];
								
								if(isset($value['expireAfter'])){
									if(!(is_int($value['expireAfter']) && $value['expireAfter']>=0))
										throw new \Exception("field '{$key}.expireAfter' must be a positive integer.");
									$o['expireAfter'] = $value['expireAfter'];
								}
								
								
								break;
							
							default:
								throw new \Exception("field '{$key}.type' : unknown.");
								
						}
						
						$value = $o;
						
					}
					else if(!is_null($value))
						throw new \Exception("field '{$key}' is invalid.");
					
					break;
					
				default:
					throw new \Exception("field '{$key}' unknown.");
			}
			
		}
		
		
		$operation = $device->operation($attributes['operation']);
		if(!$operation)
			throw new \Exception("operation '{$attributes['operation']}' does not exist.");
		
		
		return true; 
	}
	
	
	protected function call(\Ething\Event\Signal $signal){
		
		$device = $this->ething()->get( $this->device );
		if(!$device)
			throw new \Ething\InvalidRuleException("The device #{$this->device} does not exist any more");
		
		$operation = $device->operation($this->operation);
		if(!$operation)
			throw new \Exception("The device {$this->device} has no operation '{$operation}'");
		
		$buffer = new StreamBuffer();
		
		$res = $operation->call($buffer, $this->parameters, array(
			'timeout' => 5000 // 5 secondes
		));
		
		if(!$res){
			throw new \Exception($buffer->errData());
		}
		
		if(!is_null($this->output) && $buffer->length()){
			
			switch($this->output['type']){
				
				case 'file':
					
					$self = $this;
					$filename = Helpers::percent_replace($this->output['name'], function($tag) use ($signal, $self) {
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
							case '%I':
								if(isset($signal->resource)){
									return $r->resource;
								}
								break;
							case '%r':
								return $self->rule()->name;
								break;
							case '%s':
								return $signal->getName();
								break;
							case '%c':
								return (string)($self->rule()->executedCount);
								break;
						}
					});
					
					// does this file already exist !
					$file = $this->ething()->findOne(array(
						'type' => 'File',
						'name' => $filename,
						'createdBy.id' => $device->id()
					));
					if(!$file){
						// no, create it !
						$opt = array( 'name' => $filename );
						if(!empty($this->output['expireAfter']))
							$opt['expireAfter'] = $this->output['expireAfter'];
						$file = $this->ething()->create('File', $opt, $device);
					}
					if($file){
						$file->write( $buffer->data() ); // put the content in it !
					}
					
					break;
				
				case 'table':
						
					// get the data from the buffer
					$data = $buffer->decode($err);
					if(!$err){
						
						// does the table already exist ?
						$table = $this->ething()->findOne(array(
							'name' => $this->output['name'],
							'createdBy.id' => $device->id()
						));
						
						if(!$table){
							// no, so create it !
							$table = $this->ething()->create('Table', array( 'name' => $this->output['name'] ), $device);
						}
						if($table){
						
							if(is_int($data) || is_float($data) || is_string($data) || is_bool($data) || is_null($data)) // transform scalar value into array
								$data = array(
									'value' => $data
								);
							
							$table->insert($data);
						}
					}
					
					break;
				
			}
		}
		
	}
	
}



