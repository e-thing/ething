<?php
	
	namespace Ething;
	
	
	class InvalidRuleException extends \Exception {
		
		public function __construct($message = 'invalid rule') {
			parent::__construct($message, 0, null);
		}
	}
	
	