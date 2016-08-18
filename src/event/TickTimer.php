<?php

namespace Ething\Event;

class TickTimer extends Event {
	
	public function __construct(\Ething\Resource $target){
		parent::__construct($target);
	}
	
	public function description(){
		return "every minute";
	}
	
}
