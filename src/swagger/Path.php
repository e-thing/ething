<?php

namespace Ething\Swagger;



class Path {
	
	private $path;
	private $data;
	private $parent;
	
	public function __construct($path, $data, $parent) {
		
		$this->parent = $parent;
		$this->path = $path;
		$this->data = $data;
		
	}
	
	
	public function path() {
		return $this->path;
	}
	
	public function url() {
		return $this->parent->url() . $this->path;
	}
	
	public function swagger() {
		return $this->parent;
	}
	
	public function parameters() {
		
		if(!isset($this->paramters_)){
			$parameters = array();
			
			if(!empty($this->data->parameters)) {
				foreach($this->data->parameters as $param){
					$parameters[] = $param->in == 'body' ? new BodyParameter($this, $param) : new StandardParameter($this, $param);
				}
			}
			
			$this->paramters_ = $parameters;
		}
		
		return $this->paramters_;
	}
	
	public function operations() {
		if(!isset($this->operations_)){
			$operations = array();
			
			foreach($this->data as $method => $opdata){
				if(in_array($method, array('get','put','post','delete','options','head','patch'))){
					$operations[] = new Operation($method, $opdata, $this);
				}
			}
			
			$this->operations_ = $operations;
		}
		return $this->operations_;
	}
	
}
