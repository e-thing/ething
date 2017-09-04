<?php

require_once 'Stream.php';

class PoolStream {
	
	static public $streams = array();
	
	static public function add(Stream $stream){
		Log::debug("add stream ".get_class($stream));
		self::$streams[] = $stream;
	}
	
	static public function remove(Stream $stream){
		if(($key = array_search($stream, self::$streams)) !== false) {
			Log::debug("remove stream ".get_class($stream));
			array_splice(self::$streams, $key, 1);
		}
	}
	
	static public function streams(){
		$streams = array();
		foreach(self::$streams as $stream){
			$st = $stream->getStream();
			if(isset($st)){
				$streams[] = $st;
			}
		}
		return $streams;
	}
	
	static public function process($timeout = 1){
		
		$t0 = microtime(true);
		
		while(1){
			$read = self::streams();
			$write = array();
			$except = array();
			
			if(empty($read)) return;
			
			$r = @stream_select($read, $write, $except, $timeout);
			
			if($r>0){
				// incomming data
				foreach(self::$streams as $stream){
					if(in_array($stream->getStream(), $read)){
						Log::debug("data available for stream ".get_class($stream));
						$stream->process();
					}
				}
			} else {
				break; // timeout
			}
			
			if( microtime(true) - $t0 > $timeout ) break;
		}
		
		foreach(self::$streams as $stream){
			if(method_exists($stream, 'update'))
				$stream->update(); // autoconnect, ack timeout, smartSleep timeout ... 
		};
		
	}
	
	static public function each($filterFn){
		if(is_callable($filterFn)){
			foreach(self::$streams as $stream){
				if( call_user_func($filterFn, $stream) === false )
					break;
			}
		}
	}
	
	static public function find($filterFn, $limit = 0){
		$out = array();
		if(is_callable($filterFn)){
			foreach(self::$streams as $stream){
				if( call_user_func($filterFn, $stream) ){
					$out[] = $stream;
					if( $limit>0 && count($out) === $limit) break;
				}
			}
		}
		return $out;
	}
	
	static public function findOne($filterFn){
		$o = self::find($filterFn, 1);
		return count($o) ? $o[0] : null;
	}
	
	
	static public function closeAll(){
		Log::debug("close all stream");
		foreach(self::$streams as $stream){
			$str = $stream->getStream();
			if(isset($str)){
				@fclose($str);
			}
		}
	}
};
