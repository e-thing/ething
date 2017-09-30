<?php

namespace Ething\Event;

class DaemonStopped extends Event {
	
	static public function emit(){
		return new Signal('DaemonStopped');
	}
	
}
