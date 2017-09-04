<?php

namespace Ething;

class NullLogger extends Logger {
	
	protected function write($message, $level){}
	
}

