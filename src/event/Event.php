<?php

namespace Ething\Event;


use \Ething\RuleItem;
use \Ething\InvalidRuleException;

abstract class Event extends RuleItem {
	
	
	final public function match(Signal $signal){
		if($this->isValid()){
			
			// reset error
			$this->setError(false);
			
			try {
				return boolval($this->call($signal));
			}
			catch(InvalidRuleException $e){
				// this exception is fired when an action is no more valid.
				$this->setInvalid();
				$this->setError($e->getMessage());
			}
			catch(\Exception $e){
				$this->setError($e->getMessage());
			}
			
		}
		
		return false;
	}
	
	protected function call(Signal $signal) {
		return true;
	}
	
	
}


	


