<?php

namespace Ething\Event;


class FileDataModified extends AbstractResourceEvent {
	
	
	static public function emit(\Ething\File $resource){
		return new Signal('FileDataModified', array(
			'resource' => $resource->id()
		));
	}
	
	static public function validate(array &$attributes, array $context){
		$context['onlyTypes'] = array('File');
		return parent::validate($attributes, $context);
	}
}

