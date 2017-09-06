<?php

namespace Ething\Event;

class DaemonRestarted extends Event {
	
	static public function emit(){
		return new Signal('DaemonRestarted');
	}
	
}
