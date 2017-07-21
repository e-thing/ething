<?php

namespace Ething\Query;


// field<->value operator
class Operator {
	
	private $syntax;
	private $acceptField;
	private $acceptValue;
	private $compilfn;
	
	public function __construct($syntax, $compilfn, $accept = null, $acceptValue = null) {
		
		$this->syntax = $syntax;
		
		if(!isset($accept))
			$accept = '*';
		if(!isset($acceptValue))
			$acceptValue = $accept;
		
		$this->acceptField = $accept;
		$this->acceptValue = $acceptValue;
		if(is_string($this->acceptField) && $this->acceptField !== '*') $this->acceptField = array($this->acceptField);
		if(is_string($this->acceptValue) && $this->acceptValue !== '*') $this->acceptValue = array($this->acceptValue);
		
		$this->compilfn = $compilfn;
		
	}
	
	public function accept(Field $field, Value $value){
		if(!$this->acceptField($field)){
			throw new InvalidQueryException("the operator '{$this}' is not compatible with the field '{$field}'");
		}
		if($this->acceptValue !== false && !$this->acceptValue($value)){
			throw new InvalidQueryException("the operator '{$this}' is not compatible with the given value");
		}
		return true;
	}
	
	public function acceptField(Field $field){
		return $this->acceptField === '*' || $field->type()==='*' || in_array($field->type(), $this->acceptField);
	}
	
	public function acceptValue(Value $value){
		if($this->acceptValue === '*')
			return true;
		
		if($this->acceptValue === false)
			return false;
		
		foreach($this->acceptValue as $type){
			if($value->is($type)){
				return true;
			}
		}
		
		return false;
	}
	
	public function hasValue(){
		return $this->acceptValue !== false;
	}
	
	public function compil(Field $field, Value $value){
		
		$constraints = array();
		
		// type constraints (indeed, certains operators must only be applied on field with specific type
		// is it necessary ?
		if($this->acceptField !== '*'){
			foreach($this->acceptField as $type){
				switch($type){
					case 'string':
						$constraints[] = array( (string)$field => array( '$type' => 2 ) );
						break;
					case 'bool':
						$constraints[] = array( (string)$field => array( '$type' => 8 ) );
						break;
					case 'double':
						$constraints[] = array( (string)$field => array( '$type' => 1 ) );
						break;
					case 'integer':
						$constraints[] = array( (string)$field => array( '$type' => 16 ) );
						$constraints[] = array( (string)$field => array( '$type' => 18 ) );
						break;
					case 'number':
						$constraints[] = array( (string)$field => array( '$type' => 1 ) );
						$constraints[] = array( (string)$field => array( '$type' => 16 ) );
						$constraints[] = array( (string)$field => array( '$type' => 18 ) );
						break;
					case 'date':
						$constraints[] = array( (string)$field => array( '$type' => 9 ) );
						break;
					default:
						throw new InvalidQueryException("unknown type {$type}, internal error"); // internal error
				}
			}
		}
		
		$compiled = call_user_func_array( $this->compilfn, func_get_args() );
		
		return count($constraints) ? array( '$and' => array( array( '$or' => $constraints ), $compiled)) : $compiled;
		
	}
	
	public function __toString(){
		return $this->syntax;
	}
}


