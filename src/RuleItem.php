<?php

namespace Ething;


use \Ething\Rule;
use \Ething\InvalidRuleException;

abstract class RuleItem implements \JsonSerializable {
	
	
	private $_rule;
	private $_d;
	private $_isDirty = false;
	
	public function __construct(Rule $rule, array &$attributes = array()){
		$this->_d = &$attributes;
		$this->_rule = $rule;
	}
	
	public function getType() {
		return $this->_d['type'];
    }
	
	public function rule() {
		return $this->_rule;
    }
	
	public function ething() {
		return $this->rule()->ething();
    }
	
	public function isValid() {
		return empty($this->_d['isInvalid']);
    }
	
	public function setInvalid() {
		$this->_d['isInvalid'] = true;
		$this->_isDirty = true;
    }
	
	public function setError($err) {
		$err = is_string($err) ? (empty($err) ? 'unspecified error' : $err) : false;
		if( $this->_d['error'] !== $err){
			$this->_d['error'] = $err;
			$this->_isDirty = true;
		}
    }
	
	public function isDirty() {
		return $this->_isDirty;
    }
	
	public function __get($name)
    {
		return isset($this->_d['options'][$name]) ? $this->_d['options'][$name] : null;
    }
	
	public function __isset($name)
    {
		return isset($this->_d['options'][$name]);
    }
	
	public function __set($name, $value)
    {
		$this->_isDirty = true;
		$this->_d['options'][$name] = $value;
    }
	
	public function __unset($name)
    {
		unset($this->_d['options'][$name]);
    }
	
	public function jsonSerialize(){
		return $this->_d;
	}
	
	// attributes validation function
	static public function validate(array &$attributes, array $context){
		return empty($attributes); // default implementation
	}
	
}


	


