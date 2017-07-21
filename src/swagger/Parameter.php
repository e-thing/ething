<?php

namespace Ething\Swagger;



/*

todo:

allowEmptyValue
format


*/

abstract class Parameter {
	
	
	protected $data;
	protected $operation;
	
	public function __construct($operation, $data) {
		$this->operation = $operation;
		$this->data = $data;
	}
	
	public function operation() {
		return $this->operation;
	}
	
	public function swagger() {
		return $this->operation->swagger();
	}
	
	public function name() {
		return $this->data->name;
	}
	
	public function in() {
		return $this->data->in;
	}
	
	public function isRequired() {
		return !empty($this->data->required);
	}
	
	public function description() {
		return empty($this->data->description) ? '' : $this->data->description;
	}
	
	
	abstract public function validate(&$data);
	
	public function toJsonSchema() {
		return (object)array(
			'title' => $this->name(),
			'description' => $this->description()
		);
	}
	
}
