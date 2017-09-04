<?php


namespace Ething\Action;
	
class ResourceClear extends AbstractResourceAction {
	
	
	static public function validate(array &$attributes, array $context){
		
		$attributes = array_merge(
			array( 'resource' => null ),
			$attributes
		);
		
		foreach($attributes as $key => &$value){
			
			switch($key){
				
				case 'resource':
					static::validateResourceAttr($context['ething'], $value, array('File','Table'));
					break;
					
				default:
					throw new \Exception("attribute '{$key}' unknown.");
					
			}
			
		}
		
		return true; 
	}
	
	protected function call(\Ething\Event\Signal $signal){
		
		$resources = $this->getResources($signal);
		
		foreach($resources as $r){
			if($r instanceof \Ething\Table)
				$r->clear();
			else if($r instanceof \Ething\File)
				$r->write(null);
		}
		
	}
	
}


