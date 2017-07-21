<?php


namespace Ething;



class Stream {
	
	private $contentType = 'text/plain';
	private $contentLength = null;
	private $transmittedLength = 0;
	private $receivedLength = 0;
	private $inCb;
	private $outCb;
	private $closeCb;
	private $closed = false;
	private $errCode = 0;
	
	const STDOUT = 1;
	const STDERR = 2;
	
	public function __construct($inCb = null, $outCb = null, $closeCb = null){
		$this->inCb = is_callable($inCb) ? $inCb : null;
		$this->outCb = is_callable($outCb) ? $outCb : null;
		$this->closeCb = is_callable($closeCb) ? $closeCb : null;
	}
	
	public function contentType($contentType = null){
		if(is_string($contentType))
			$this->contentType = $contentType;
		return $this->contentType;
	}
	
	public function contentLength(){
		return is_null($this->contentLength) ? -1 : $this->contentLength;
	}
	
	public function errCode($errCode = null){
		if(is_int($errCode))
			$this->errCode = $errCode;
		return $this->errCode;
	}
	
	public function transmittedLength(){
		return $this->transmittedLength;
	}
	
	public function receivedLength(){
		return $this->receivedLength;
	}
	
	public function in(){
		if($this->closed) return;
		return ($this->inCb !== null) ? call_user_func($this->inCb, $this) : '';
	}
	
	public function out($data, $no = Stream::STDOUT){
		if($this->closed) return;
		if(!is_string($data)){
			$data = \json_encode($data, JSON_PRETTY_PRINT);
			if($data===false){
				return $this->err('invalid data');
			}
			$this->contentType('application/json');
		}
		$len = strlen($data);
		$this->receivedLength += $len;
		if($this->outCb !== null)
			call_user_func($this->outCb, $this, $data, $no);
		return $len;
	}
	
	public function err($data){
		return $this->out($data, Stream::STDERR);
	}
	
	public function close($errCode = null, $errMessage = null){
		if($this->closed) return;
		
		if(isset($errCode)) $this->errCode($errCode);
		
		if(isset($errMessage)){
			$this->err(array(
				'message' => $errMessage,
				'code' => $this->errCode()
			));
		}else if($this->receivedLength===0){
			$this->out(''); // force to execute the out callback at least 1 time. Very useful for sending http headers when there is an empty body.
		}
		
		if($this->closeCb !== null)
			call_user_func($this->closeCb, $this, $this->errCode());
		$this->closed = true;
	}
	
}

