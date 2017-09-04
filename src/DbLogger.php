<?php

namespace Ething;

class DbLogger extends Logger {
	
	private $coll = null;
	
	protected function layout($message, $level) {
		return $message;
	}
	
	protected function write($message, $level){
		
		$this->open();
		
		$this->coll->insertOne(array(
			'level' => $level,
			'name' => $this->name,
			'date' => new \MongoDB\BSON\UTCDateTime(time()*1000),
			'message' => $message
		));
		
	}
	
	private function open(){
		if(!isset($this->coll)){
			$this->coll = $this->ething->db()->selectCollection('log');
			
			if($this->coll->count()===0){
				$this->ething->db()->createCollection("log", array(
					'capped' => true,
					'size' => 1024000,
					'max' => 1000
				));
			}
		}
	}
	
	
	public function read($limit = 0){
		
		$this->open();
			
		$opt = array();
		
		$opt['sort'] = array('$natural'=>-1);
		if($limit)
			$opt['limit'] = $limit;
		
		return array_map(function($l){
			return $l['date']->toDateTime()->format("Y-m-d H:i:s").' '.$l['name'].' '.Logger::$levelToStr[$l['level']].' - '.$l['message'];
		}, $this->coll->find(array(), $opt)->toArray());
	}
	
	
}

