<?php


class StreamCollection {
	
	public $streams = array();
	
	public function add($stream){
		if($stream) {
			$this->streams[] = $stream;
			return true;
		}
		return false;
	}
	
	public function remove($stream){
		
		if(($key = array_search($stream, $this->streams)) !== false) {
			array_splice($this->streams, $key, 1);
		}
		
	}
	
	public function length(){
		$c = 0;
		foreach($this->streams as $stream){
			if(isset($stream->stream)){
				$c++;
			}
		}
		return $c;
	}
	
	public function streams(){
		$streams = array();
		foreach($this->streams as $stream){
			if(isset($stream->stream)){
				$streams[] = $stream->stream;
			}
		}
		return $streams;
	}
	
	
	public function available(&$streams, $timeout = 1){
		$streams = array();
		$read = $this->streams();
		$write = array();
		$except = array();
		
		if(empty($read)) return false;
		
		$r = @stream_select($read, $write, $except, $timeout);
		
		if($r>0){
			// incomming data
			foreach($this->streams as $stream){
				if(in_array($stream->stream, $read))
					$streams[] = $stream;
			}
		}
		
		return $r>0;
	}
	
	public function each($filterFn){
		if(is_callable($filterFn)){
			foreach($this->streams as $stream){
				if( call_user_func($filterFn, $stream) === false )
					break;
			}
		}
	}
	
	public function find($filterFn){
		$out = array();
		if(is_callable($filterFn)){
			foreach($this->streams as $stream){
				if( call_user_func($filterFn, $stream) )
					$out[] = $stream;
			}
		}
		return $out;
	}
	
	public function findOne($filterFn){
		$o = self::find($filterFn);
		return count($o) ? $o[0] : null;
	}
	
};
