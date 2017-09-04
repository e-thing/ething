<?php

namespace Ething;

class ConsoleLogger extends Logger {
	
	protected function write($message, $level){
		fwrite($level <= Logger::INFO ? STDERR : STDOUT, $message.PHP_EOL);
	}
	
}

