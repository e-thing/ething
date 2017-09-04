<?php


namespace Ething;


use \Ething\Helpers;


class Request {
	
	public $url;
	private $method = 'GET';
	public $body = '';
	private $headers = array();
	
	public static $validAuthModes = array('basic', 'digest', 'query'); 
	public static $validMethodes = array('get','post','put','patch','head','options','delete'); 
	
	public function __construct( $url, $method = 'GET', array $headers = array(), $body = '' ){
		$this->url = ($url instanceof Url) ? $url : new Url($url);
		$this->setMethod($method);
		$this->setHeaders($headers);
		$this->body = $body;
	}
	
	public function getMethod(){
		return $this->method;
	}
	
	public function setMethod($method){
		$this->method = strtoupper($method);
	}
	
	public function getHeaders(){
		return $this->headers;
	}
	
	public function getHeader($name){
		$name = strtolower($name);
		return isset($this->headers[$name]) ? $this->headers[$name] : null;
	}
	
	public function setHeaders(array $headers){
		
		if(Helpers::is_numeric_array($headers)){
			// each value correspond to a header line
			$m = array();
			foreach($headers as $h){
				
				if(is_object($h)) $h = (array)$h;
				
				if(is_string($h)){
					if(preg_match('/^ *([^:]*) *: *(.+)$/', $h, $matches)){
						$m[$matches[1]] = $matches[2];
					}
				} else if(is_array($h) && array_key_exists('key', $h) && array_key_exists('value', $h)){
					$m[$h['key']] = $h['value'];
				}
			}
			$headers = $m;
		}
		
		$this->headers = array_change_key_case($headers, CASE_LOWER);
	}
	
	public function addHeader($name, $value){
		$this->headers[strtolower($name)] = $value;
	}
	
	public function removeHeader($name){
		unset($this->headers[strtolower($name)]);
	}
	
	public function contentType(){
		return isset($this->headers['content-type']) ? $this->headers['content-type'] : null;
	}
	
	public function toString(){
		$s = "{$this->method} ".$this->url." HTTP/1.1".PHP_EOL;
		foreach($this->headers as $name => $value){
			$s .= "{$name}: {$value}".PHP_EOL;
		}
		$s .= PHP_EOL;
		$s .= $this->body;
		return $s;
	}
	
	static public function createFromGlobals( $url = null ){
		
		if(!isset($url))
			$url = Url::current();
		
		$request = new Request( $url );
		
		$request->setMethod($_SERVER['REQUEST_METHOD']);
		
		$request->body = file_get_contents('php://input');
		
		foreach($_SERVER as $name => $value){
			
			if ( 'CONTENT_TYPE' === $name ) $name = 'HTTP_'.$name;
			
			if(strpos($name, 'HTTP_') === 0){
				$name = substr($name, 5);
				$name = str_replace('_', ' ', $name);
				$name = ucwords(strtolower($name));
				$name = str_replace(' ', '-', $name);
				
				$request->addHeader($name, $value);
			}
		}
		
		return $request;
	}
	

}

