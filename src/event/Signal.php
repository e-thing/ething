<?php

namespace Ething\Event;


class Signal implements \JsonSerializable {
	
	private $_ts;
	private $_d; // data
	private $_name;
	private $_propagationStopped = false;
	
	public function __construct($name, array $attributes = array())
	{
		$this->_name = $name;
		$this->_d = $attributes;
		$this->_ts = time();
	}
	
	public function getName()
	{
		return $this->_name;
	}
	
	public function getTimestamp()
	{
		return $this->_ts;
	}
	
	public function getAttributes()
	{
		return $this->_d;
	}
	
	public function __get($name)
    {
		return isset($this->_d[$name]) ? $this->_d[$name] : null;
    }
	
	public function __isset($name)
    {
		return isset($this->_d[$name]);
    }
	
	public function __toString()
    {
		return $this->getName();
    }
	
	public function stopPropagation()
	{
		$this->_propagationStopped = true;
	}
	
	public function isPropagationStopped()
	{
		return $this->_propagationStopped;
	}
	
	public function debugStr() {
		return "Signal: {$this->getName()} data: ".json_encode($this->_d);
	}
	
	public function jsonSerialize(){
		return array(
			'name' => $this->_name,
			'ts' => $this->_ts,
			'data' => empty($this->_d) ? null : $this->_d
		);
	}
	
}



