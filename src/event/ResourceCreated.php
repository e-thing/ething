<?php

namespace Ething\Event;


class ResourceCreated extends AbstractResourceEvent {
	
	static public function emit(\Ething\Resource $resource){
		return new Signal('ResourceCreated', array(
			'resource' => $resource->id()
		));
	}
	
}

