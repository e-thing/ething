<?php

namespace Ething\Swagger;



/*

todo:

allowEmptyValue
format


*/

class StandardParameter extends Parameter {
	
	static private $collectionFormat = array(
		'csv' => ",",
		'ssv' => " ",
		'tsv' => "\t",
		'pipes' => "|"
	);
	
	
	public function type() {
		return $this->data->type;
	}
	public function hasDefault() {
		return isset($this->data->default);
	}
	
	public function geDefaultValue() {
		return $this->data->default;
	}
	
	public function collectionFormat() {
		return $this->data->collectionFormat;
	}
	
	public function validate(&$data) {
		
		static::validateType((array)$this->data, $data, true);
		
		return true;
	}
	
	
	static private $jsonSchemaFields = array(
		'type',
		'format',
		'items',
		'default',
		'maximum',
		'exclusiveMaximum',
		'minimum',
		'exclusiveMinimum',
		'maxLength',
		'minLength',
		'pattern',
		'maxItems',
		'minItems',
		'uniqueItems',
		'enum',
		'multipleOf'
	);
	
	
	static private function filter($schema, $in = null){
		
		if($in === null)
			$in = new \StdClass();
		
		foreach(static::$jsonSchemaFields as $field){
			if(isset($schema->$field)){
				$in->$field = ($field == 'items') ? static::filter($schema->$field) : $schema->$field;
			}
		}
		
		return $in;
	}
	
	public function toJsonSchema() {
		// replace by a deep clone
		return static::filter($this->data, parent::toJsonSchema());
	}
	
	
	// value will be transformed into a string
	static private function validateType(array $options, &$value){
		$type = $options['type'];
		
		if((!isset($value) || $value==='') && !empty($options['allowEmptyValue']))
			return true;
		
		switch($type){
			
			case "string":
				
				if(!is_string($value))
					throw new Exception("must be a string '${value}'");
				
				break;
			case "number":
				
				if(!is_numeric($value))
					throw new Exception("must be a number '${value}'");
				
				$value = $value+0;
				
				break;
			case "integer":
				
				if(!is_int($value) && !(is_numeric($value) && preg_match("/^[+\-]?[0-9]+$/D", $value)))
					throw new Exception("must be an integer '${value}'");
				
				$value = $value+0;
				
				break;
			case "boolean":
				
				if($value===true || (is_string($value) && ( strtolower($value)==='true' || $value === '1' ) ))
					$value = true;
				else if($value===false || (is_string($value) && ( strtolower($value)==='false' || $value === '0' ) ))
					$value = false;
				else
					throw new Exception("must be a boolean '${value}'");
				
				break;
			case "array":
				
				if(!is_array($value))
					throw new Exception("must be an array '${value}'");
				
				foreach($value as &$v){
					static::validateType((array)$options['items'], $v);
				}
				
					
				$collectionFormat = empty($options['collectionFormat']) ? 'csv' : $options['collectionFormat'];
				
				if(array_key_exists($collectionFormat, static::$collectionFormat))
					$value = implode( static::$collectionFormat[$collectionFormat], $value);
				
				break;
			case "file":
				
				if(!is_string($value))
					throw new Exception("must be a string '${value}'");
				
				break;
			
		}
		
		if(!is_string($value))
			$value = (string) $value;
		
		return true;
	}
	
}
