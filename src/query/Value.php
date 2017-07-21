<?php

namespace Ething\Query;



class Value {
	
	private $value;
	
	public function __construct($value = null) {
		$this->value = $value;
	}
	
	// return the intrinsec type : boolean, integer, double, string, ...
	public function type(){
		return gettype($this->value);
	}
	
	// check if the value has the given type
	public function is($type){
		switch(strtolower($type)){
			case 'string':
			case 'boolean':
			case 'double':
			case 'integer':
				return $this->type()===$type;
			case 'bool':
				return $this->type()==='boolean';
			case 'number':
				return $this->type()==='integer' || $this->type()==='double';
			case 'date':
				return $this->type()==='string' && \date_create($this->value) !== false;
			case 'null':
				return $this->type()==='NULL';
			default:
				throw new InvalidQueryException("unknown type {$type}");
		}
	}
	
	public function getValue(){
		return $this->value;
	}
	
	public function getDate(){
		$date = \date_create($this->value);
		if($date !== false){
			return $date;
		}
		throw new InvalidQueryException("invalid date '{$this->value}'",$stream);
	}
	
	public function __toString(){
		return $this->value;
	}
}


