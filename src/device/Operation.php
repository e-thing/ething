<?php

namespace Ething\Device;

use \Ething\Stream;

class Operation implements \JsonSerializable {
	
	private $device_;
	private $name_;
	private $schema_;
	private $parameters_;
	private $response_;
	private $call_;
	
	public static function emptySchema(){
		$o = new \stdClass();
		$o->type = "object";
		$o->additionalProperties = false;
		$o->properties = new \stdClass();
		return $o;
	}
	
	public function __construct(Device $device, $name, \stdClass $schema = null, $response = null, $description = null, $call = null) {
		$this->device_ = $device;
		$this->name_ = $name;
		$this->schema_ = isset($schema) ? $schema : self::emptySchema();
		$this->description_ = $description;
		$this->response_ = $response;
		$this->call_ = $call;
	}
	
	public function __toString(){
		return $this->name();
	}
	
	public function name() {
		return $this->name_;
	}
	
	public function ething() {
		return $this->device_->ething;
	}
	
	public function device() {
		return $this->device_;
	}
	
	public function schema() {
		return $this->schema_;
	}
	
	public function description() {
		return empty($this->description_) ? '' : $this->description_;
	}
	
	public function response() {
		return $this->response_;
	}
	
	public function call(Stream $stream = null, array $data = null, array $options = array()){
		if(is_callable($this->call_)){
			$r = call_user_func($this->call_, $this, $stream, $data, $options);
			if(isset($stream)){
				if($r===false) $stream->errCode(1);
				$stream->close();
			}
			return $r;
		}
		return false;
	}
	
	public function jsonSerialize() {
		return array(
			'name' => $this->name_,
			'description' => $this->description(),
			'device' => array(
				'type' => $this->device_->type(),
				'id' => $this->device_->id()
			),
			'schema' => $this->schema(),
			'response' => $this->response()
		);
	}
	
}
