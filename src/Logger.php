<?php

namespace Ething;

abstract class Logger {
	
	const TRACE = 0;
	const DEBUG = 1;
	const INFO  = 2;
	const WARN  = 3;
	const ERROR = 4;
	const FATAL = 5;
	
	
	
	protected static $levelToStr = array('TRACE','DEBUG','INFO','WARN','ERROR','FATAL');
	
	private static $loggers = array();
	
	public static function getLogger($name){
		if(!isset(Logger::$loggers[$name])){
			Logger::$loggers[$name] = new Logger($name);
		}
		return Logger::$loggers[$name];
	}
	
	public static function setLogger($name, Logger $logger){
		Logger::$loggers[$name] = $logger;
	}
	
	
	public $ething;
	protected $name;
	protected $level = self::INFO;
	
	public function __construct(Ething $ething, $name, $level = self::INFO){
		$this->ething = $ething;
		$this->name = $name;
		if(isset($level)) $this->level = $level;
	}
	
	public function setName($name){
		$this->name = $name;
	}
	
	public function getName(){
		return $this->name;
	}
	
	public function setLevel($level){
		$this->level = $level;
	}
	
	public function getLevel(){
		return $this->level;
	}
	
	abstract protected function write($message, $level); 
	
	protected function render($message, $level){
		// message render
		if(is_string($message)) {
			$renderedMessage = $message;
		} else if($message instanceof \Exception) {
			//$renderedMessage = (string) $message;
			$renderedMessage = $message->getMessage()." [file:".$message->getFile()." line:".$message->getLine()."]"; // do not print the stack
		} else {
			$renderedMessage = print_r($message, true);
		}
		return $renderedMessage;
	}
	
	protected function layout($message, $level) {
		return date("Y-m-d H:i:s").' '.$this->name.' '.Logger::$levelToStr[$level].' - '.$message;
	}
	
	private function log($level, $message, $force = false){
		if($level >= $this->level || $force){
			$this->write($this->layout($this->render($message, $level), $level), $level);
		}
	}
	
	public function trace($message){
		return $this->log(self::TRACE, $message);
	}
	
	public function debug($message){
		return $this->log(self::DEBUG, $message);
	}
	
	public function info($message){
		return $this->log(self::INFO, $message);
	}
	
	public function warn($message){
		return $this->log(self::WARN, $message);
	}
	
	public function error($message){
		return $this->log(self::ERROR, $message);
	}
	
	public function fatal($message){
		return $this->log(self::FATAL, $message);
	}
	
	public function force($message){
		return $this->log(self::INFO, $message, true);
	}
	
	
	public function read($limit = 0){
		return array();
	}
}

