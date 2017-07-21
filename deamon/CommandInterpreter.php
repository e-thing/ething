<?php

require_once 'Client.php';

class CommandInterpreter {
	
	
	protected $commands = array();
	
	public function add($command, $call){
		if(is_callable($call)){
			$this->commands[$command] = $call;
		}
	}
	
	
	public function run($command, $args, Client $client){
		
		if(array_key_exists($command, $this->commands)){
			return call_user_func($this->commands[$command], $args, $client);
		} else {
			throw new Exception("unknown command '{$command}'");
		}
		
	}
	
	
};

