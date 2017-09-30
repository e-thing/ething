<?php

namespace Ething\Event;

class DaemonStarted extends Event {
	
	static public function emit(){
		return new Signal('DaemonStarted');
	}
	
}
