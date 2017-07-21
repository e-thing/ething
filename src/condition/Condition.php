<?php


namespace Ething\Condition;

use \Ething\RuleItem;
use \Ething\InvalidRuleException;
use \Ething\Event\Signal;

abstract class Condition extends RuleItem {
	
	
	final public function evaluate(Signal $signal){
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
	
	abstract protected function call(\Ething\Event\Signal $signal);
	
	
}


	

