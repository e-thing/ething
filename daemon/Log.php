<?php


class Log {
	
	const TRACE = 0;
	const DEBUG = 1;
	const INFO  = 2;
	const WARN  = 3;
	const ERROR = 4;
	const FATAL = 5;
	
	
	
	static protected $levelToStr = array('TRACE','DEBUG','INFO','WARN','ERROR','FATAL');
	
	static protected $level = self::INFO;

	static protected $name = 'LOG';
	
	static public $ething = null;
	
	static public function setName($name){
		if(is_string($name))
			self::$name = $name;
	}
	
	static public function getName(){
		return self::$name;
	}
	
	static public function setLevel($level){
		if($level>=0 && $level<=5)
			self::$level = $level;
	}
	
	static public function getLevel(){
		return self::$level;
	}
	
	static protected function write($message, $level){
		fwrite($level <= Log::INFO ? STDERR : STDOUT, $message);
	}
	
	static protected function render($message, $level){
		// message render
		if(is_string($message)) {
			$renderedMessage = $message;
		} else if($message instanceof \Exception) {
			$renderedMessage = (string) $message;
		} else {
			$renderedMessage = print_r($message, true);
		}
		return $renderedMessage;
	}
	
	static protected function layout($message, $level) {
		return date("Y-m-d H:i:s").' '.self::$name.' '.Log::$levelToStr[$level].' - '.$message.PHP_EOL;
	}
	
	static private function _log($level, $message, $force = false){
		if($level >= self::$level || $force){
			self::write(self::layout(self::render($message, $level), $level), $level);
		}
		
		if(isset(self::$ething))
			self::$ething->logger()->log($level, $message, $force);
	}
	
	static public function trace($message){
		return self::_log(Log::TRACE, $message);
	}
	
	static public function debug($message){
		return self::_log(Log::DEBUG, $message);
	}
	
	static public function info($message){
		return self::_log(Log::INFO, $message);
	}
	
	static public function warn($message){
		return self::_log(Log::WARN, $message);
	}
	
	static public function error($message){
		return self::_log(Log::ERROR, $message);
	}
	
	static public function fatal($message){
		self::_log(Log::FATAL, $message);
		exit(3);
	}
	
	static public function force($message){
		return self::_log(Log::INFO, $message, true);
	}
	
};

