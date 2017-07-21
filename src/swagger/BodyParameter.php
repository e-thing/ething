<?php

namespace Ething\Swagger;



/*

todo:

allowEmptyValue
format


*/

class BodyParameter extends Parameter {
	
	
	static private $nonJsonSchemaFields = array(
		'discriminator',
		'readOnly',
		'xml',
		'externalDocs',
		'example'
	);
	
	private $schema;
	
	public function __construct($operation, $data) {
		
		parent::__construct($operation, $data);
		
		$this->schema = $this->data->schema;
		
	}
	
	public function schema() {
		return $this->schema;
	}
	
	public function validate(&$data) {
		
		static::validateSchema((array)$this->data, $data);
		
		return true;
	}
	
	public function toJsonSchema() {
		$jsonSchema = (object) array_replace((array) parent::toJsonSchema(), (array) $this->swagger()->resolveRef($this->schema));
		return $jsonSchema;
	}
	

	static private function validateSchema(array $options, &$value, $definitions = array()){
		// todo !
	}
	
}
