<?php


namespace Ething\Action;

use \Ething\Helpers;

class Notify extends Action {
	
	
	// attributes validation function
	static public function validate(array &$attributes, array $context){
		
		$attributes = array_merge(
			array( 'subject' => "Notification from e-Thing", 'content' => 'no content', 'attachments' => null ),
			$attributes
		);
		
		foreach(array_keys($attributes) as $key){
			
			switch($key){
				
				case 'subject':
				case 'content':
				
					if(!is_string($attributes[$key]))
						throw new \Exception("field '{$key}' must be a string.");
					
					if(empty($attributes[$key]))
						throw new \Exception("field '{$key}' must be set.");
					
					break;
					
				case 'attachments':
					AbstractResourceAction::validateResourceAttr($context['ething'], $attributes[$key], array('File','Table'));
					break;
				
				default:
					throw new \Exception("field '{$key}' unknown.");
			}
			
		}
		
		return true; 
	}
	
	
	protected function call(\Ething\Event\Signal $signal){
		$self = $this;
		
		$content = Helpers::percent_replace($this->content, function($tag) use ($signal, $self) {
			switch($tag){
				case '%%':
					return '%';
				case '%D':
					return date("Y-m-d H:i:s", $signal->getTimestamp());
				case '%R':
					if(isset($signal->resource)){
						if($r = $self->ething()->get($signal->resource))
							return $r->name();
					}
					break;
				case '%I':
					if(isset($signal->resource)){
						return $r->resource;
					}
					break;
				case '%d':
					if(isset($signal->data)){
						return json_encode($signal->data, JSON_PRETTY_PRINT|JSON_UNESCAPED_SLASHES);
					}
					break;
				case '%r':
					return $self->rule()->name;
					break;
				case '%s':
					return $signal->getName();
					break;
			}
		});
		
		$attachments = array();
		try {
			$rs = AbstractResourceAction::getResourcesStatic($this->ething(), $this->attachments);
		} catch(\Exception $e){
			$this->setError($e->getMessage());
		}
		if(!empty($rs)){
			foreach( $rs as $r){
				
				if($r instanceof \Ething\File){
					$attachments[] = array(
						'name' => \basename($r->name()),
						'content' => $r->read(),
						'type' => $r->mime
					);
				} else if($r instanceof \Ething\Table){
					$attachments[] = array(
						'name' => \preg_replace('/\\.[^.\\s]$/', '', \basename($r->name())).'.json',
						'content' => \json_encode($r->select(), JSON_PRETTY_PRINT|JSON_UNESCAPED_SLASHES),
						'type' => 'application/json'
					);
				}
			}
		}
		
		$this->ething()->notify($this->subject,$content,$attachments);
	}
	
}


