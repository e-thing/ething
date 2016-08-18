<?php


namespace Ething\Action;
	
class Notify extends Action {
	
	public $subject;
	public $content;
	
	// this action is compatible with all events and all resource
	static public function check(array &$json, $eventName, $resourceTypeName){
		
		if(isset($json['subject']) && (!is_string($json['subject']) || empty($json['subject'])))
			throw new \Ething\Exception('invalid value for the field "subject"');
		
		if(isset($json['content']) && (!is_string($json['content']) || empty($json['content'])))
			throw new \Ething\Exception('invalid value for the field "content"');
		
		return true;
	}
	
	public function execute(\Ething\Event\Event $event, \Ething\Rule $rule){
		
		$subject = empty($this->subject) ? ("Notification from ".$event->target()->name()) : $this->subject;
		
		if(empty($this->content)){
			$body = "This notification was sent from '<b>".$event->target()->name()."</b>'<br>";
			$body .= $event->description()."<br>";
			$body .= implode('<br> and ',array_map(function($condition){
				return $condition->description();
			}, $rule->conditions()));
		}
		else
			$body = $content;
		
		$event->target()->user()->sendMail($subject,$body);
		
	}
	
}


