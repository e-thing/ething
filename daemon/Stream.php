<?php


abstract class Stream {
	
	
	private $streams = array();
	private $ids = array();
	
	public function registerStream($stream, $id = null){
		if(!isset($id)) $id = count($this->ids);
		$this->streams[] = $stream;
		$this->ids[] = $id;
		return $id;
	}
	
	public function getRegisteredStream($id){
		foreach($this->ids as $i => $v){
			if($id === $v){
				return $this->streams[$i];
			}
		}
	}
	
	
	public function unregister($id){
		foreach($this->ids as $i => $v){
			if($id === $v){
				unset($this->streams[$i]);
				unset($this->ids[$i]);
			}
		}
	}
	
	public function unregisterAll(){
		$this->streams = array();
		$this->ids = array();
	}
	
	public function getRegisteredStreams(){
		return $this->streams;
	}
	
	public function onSocketActivity($index){
		$this->process($this->streams[$index], $this->ids[$index]);
	}
	
	public function closeAndUnregisterAll(){
		foreach($this->streams as $i => $s){
			@fclose($s);
		}
		$this->unregisterAll();
	}
	
	abstract public function process($resource, $id);
	
};
