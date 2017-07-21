<?php

namespace Ething\Swagger;



class Client {
	
	private $data; // hold the specification
	
	
	public function __construct($specification) {
		
		if(is_string($specification)){
			$this->data = json_decode($specification);
		}
		else if(is_array($specification)){
			$this->data = json_decode(json_encode($specification));
		}
		else {
			$this->data = $specification;
		}
		
		if($this->version() != '2.0')
			throw new Exception('Only 2.0 swagger specification is accepted.');
		
	}
	
	public function version() {
		return $this->data->swagger;
	}
	
	public function produces() {
		return empty($this->data->produces) ? array() : $this->data->produces;
	}
	
	public function consumes() {
		return empty($this->data->consumes) ? array() : $this->data->consumes;
	}
	
	public function host() {
		return empty($this->data->host) ? 'localhost' : $this->data->host;
	}
	
	public function basePath() {
		return empty($this->data->basePath) ? '' : $this->data->basePath;
	}
	
	public function schemes() {
		return empty($this->data->schemes) ? array('http') : $this->data->schemes;
	}
	
	public function url() {
		return $this->schemes()[0] .'://' . $this->host() .  $this->basePath();
	}
	
	// return a reference
	public function getRef($ref){
		
		if(preg_match('@^#/[^/]+/.+@', $ref)){
			
			$parts = explode('/', $ref);
			
			array_shift($parts);
			
			$obj = $this->data;
			while(count($parts)){
				$attr = array_shift($parts);
				if(property_exists($obj, $attr)){
					if(is_object($obj->$attr)) {
						$obj = $obj->$attr;
					} else
						throw new Exception("invalid reference {$ref}");
				} else
					throw new Exception("reference not found {$ref}");
			}
			
			return $obj;
		}
		else
			throw new Exception("invalid reference {$ref}");
	}
	
	public function resolveRef($value){
		
		if(is_object($value)) {
			
			if(isset($value->{'$ref'})){
				$o = $this->resolveRef($this->getRef($value->{'$ref'}));
			} else {
				$o = new \StdClass();
				foreach(get_object_vars($value) as $f => $v){
					$o->{$f} = $this->resolveRef($v);
				}
			}
			
		} else if(is_array($value)) {
			$o = array();
			foreach( $value as $k => $v ){
				$o[$k] = $this->resolveRef($v);
			}
		} else {
			$o = $value;
		}
		
		return $o;
			
	}
	
	
	// return all the operations
	public function operations() {
		if(!isset($this->operations_)){
			$operations = array();
			
			foreach($this->paths() as $path)
				$operations = array_merge($operations, $path->operations());
			
			$this->operations_ = $operations;
		}
		return $this->operations_;
	}
	
	public function findOperationById($id) {
		foreach($this->operations() as $operation){
			if($operation->name() === $id)
				return $operation;
		}
		return null;
	}
	
	public function paths() {
		if(!isset($this->paths_)){
			$paths = array();
			
			foreach($this->data->paths as $path => $pathdata){
				$paths[] = new Path($path, $pathdata, $this);
			}
			
			$this->paths_ = $paths;
		}
		return $this->paths_;
	}
	
	
	
	
}
