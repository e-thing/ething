<?php

namespace Ething\Event;


class ResourceDeleted extends AbstractResourceEvent {
	
	static public function emit(\Ething\Resource $resource){
		return new Signal('ResourceCreated', array(
			'resource' => $resource->id()
		));
	}
	
}

