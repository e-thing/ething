<?php

namespace Ething\Query;



class Stream {
	
	private $index = 0;
	private $index_last = 0;
	private $content = '';
	
	public function __construct($content) {
		if(is_string($content)){
			$this->content = $content;
		}
	}
	
	public function currentIndex(){
		return $this->index;
	}
	
	public function previousIndex(){
		return $this->index_last;
	}
	
	public function walk($numberOfChar){
		if($numberOfChar>0){
			$length = strlen($this->content);
			if($numberOfChar<$length){
				$this->content = substr($this->content,$numberOfChar);
			}
			else {
				$numberOfChar = $length;
				$this->content = '';
			}
		}
		$this->index_last = $this->index;
		$this->index += $numberOfChar;
		return $numberOfChar;
	}
	
	public function read($a){
		if(is_int($a) && $a>0){
			// read n characters
			$o = substr($this->content, 0, $a);
			$this->walk(strlen($o));
			return $o;
		}
		else if(is_string($a)){
			// return the first match
			if(preg_match($a,$this->content,$match,PREG_OFFSET_CAPTURE)){
				$o = $match[0][0];
				$this->walk(strlen($o)+$match[0][1]);
				return $o;
			}
			else
				$this->walk(0);// just for updating the $index_last property
		}
		return null;
	}
	
	public function match($regex){
		return (bool) preg_match($regex,$this->content);
	}
	
	public function skipSpace(){
		return $this->read('/^\s*/');
	}
	
	public function readWord(){
		return $this->read('/[^\s]+/');
	}
	
	public function length(){
		return strlen($this->content);
	}
	
	public function __toString(){
		return $this->content;
	}
}


