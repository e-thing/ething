<?php


namespace Ething;



class Response {
	
	private $status = 0;
	public $body = '';
	private $headers = array();
	
	public function __construct(){}
	
	public function getStatus(){
		return $this->status;
	}
	
	public function isSuccessful(){
		return $this->status >= 200 && $this->status < 300;
	}
	
	public function setStatus($status){
		$this->status = intval($status);
	}
	
	public function getHeader($name){
		$name = strtolower($name);
		return isset($this->headers[$name]) ? $this->headers[$name] : null;
	}
	
	public function setHeaders(array $headers){
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
		$s = "HTTP/1.1 {$this->status} ".PHP_EOL;
		foreach($this->headers as $name => $value){
			$s .= "{$name}: {$value}".PHP_EOL;
		}
		$s .= PHP_EOL;
		$s .= $this->body;
		return $s;
	}
	
	// write the headers to output
	public function sendHeader(){
		if(headers_sent()){
			return;
		}
		
		http_response_code($this->status);
		
		foreach($this->headers as $name => $value){
			header(sprintf("%s: %s", $name, $value));
		}
	}
	
	// write the whole response to the output
	public function send(){
		$this->sendHeader();
		echo $this->body;
	}
	

}

