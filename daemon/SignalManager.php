<?php

class SignalManager {
	
	static private $handlers = array();
	
	
	static public function dispatch(\Ething\Event\Signal $signal){
		
		Log::debug("dispatchSignal => {$signal->debugStr()}");
		
		foreach(self::$handlers as $handler){
			call_user_func($handler, $signal);
		}
		
	}
	
	static public function attachHandler($handler){
		if(is_callable($handler)){
			self::$handlers[] = $handler;
		}
	}
	
	
};
