<?php
	
	namespace Ething;
	
	
	class Exception extends \Exception {
		// default return code is 400 (= Bad Request)
		public function __construct($message, $code = 400, \Exception $previous = null) {
			parent::__construct($message, $code, $previous);
		}
	}
	
	