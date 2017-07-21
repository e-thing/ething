<?php


namespace Ething;



class StreamBuffer extends Stream {
	
	private $data = '';
	private $errData = '';
	
	
	public function writeFn($stream, $chunk, $no){
		if($no === 2) // stderr
			$this->errData .= $chunk;
		else // stdout
			$this->data .= $chunk;
	}
	
	public function __construct($closeCb = null){
		parent::__construct( null, array($this, 'writeFn'), $closeCb);
	}
	
	public function data(){
		return $this->data;
	}
	
	public function length(){
		return strlen($this->data);
	}
	
	public function errData(){
		return $this->errData;
	}
	
	// if there is some json in the buffer, decode it as a php variable
	public function decode(&$error = null){
		
		$error = true;
		
		switch(strtolower($this->contentType())){
			case 'text/plain':
				
				$error = false;
				return $this->data;
				
			case 'application/json': 
				
				$decoded_data = \json_decode($this->data, true);
				
				if(\json_last_error() === JSON_ERROR_NONE){
					$error = false;
					return $decoded_data;
				}
				
				break;
			case 'application/x-www-form-urlencoded':
				
				\parse_str($this->data, $decoded_data);
				$error = false;
				return $decoded_data;
				
				
		}
		
	}
	
	public function __toString() {
        return $this->data;
    }
	
	
	
}

