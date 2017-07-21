<?php


require_once 'CommandInterpreter.php';


class Client {
	
	public $stream = null;
	public $isOpened = false;
	private $buffer = '';
	public $id = 0;
	
	private $commandInterpreter = null;
	
	public function __construct($stream, CommandInterpreter $ci){
		$this->id = rand();
		$this->commandInterpreter = $ci;
		// make this stream non blocking !
		stream_set_blocking($stream, false);
		$this->stream = $stream;
		$this->isOpened = true;
		$this->write(">");
	}
	
	public function write($str){
		return $this->isOpened ? @fwrite($this->stream, $str) : 0;
	}
	
	public function read(){
		global $streams, $ething;
		
		if($this->isOpened){
			
			$chunk = fgets($this->stream);
			if($chunk===false){
				// an error occurs
				$this->close();
				return;
			}
			$this->buffer .= $chunk;
			
			//uecho(strlen($chunk));
			if(strlen($chunk) === 0){
				// connection closed
				$this->close();
				
			} else if(false !== ($p = strrpos($this->buffer, "\n")) ){
				
				$lines = preg_split("/\r?\n/", substr($this->buffer, 0, $p+1));
				$this->buffer = substr($this->buffer, $p+1);
				
				foreach($lines as $line){
					
					$line = trim($line);
					if(empty($line)) continue;
					
					try{
						$args = static::parseArgs($line);
						$cmd = array_shift($args);
						$this->commandInterpreter->run($cmd, $args, $this);
					} catch(\Exception $e){
						$this->error($e);
					}
					
					
				}
				
			}
		}
		
	}
	
	
	static private function parseArgs($line){
		$args = array();
		$carg = '';
		$escaped = false;
		$slashEscaped = false;
		
		$line .= ' '; // add a trailing space
		
		for($i=0; $i<strlen($line); $i++){
			
			$c = $line[$i];
			$skip = false;
			
			if(!$slashEscaped && ($c=='"' || $c=="'")){
				if($escaped===$c){
					$escaped = false;
					$skip = true;
				} else if(!$escaped){
					$escaped = $c;
					$skip = true;
				}
			} else if($c=='\\' && !$slashEscaped){
				$skip = true;
				$slashEscaped=$c;
			} else if($c==' ' && !$escaped && !$slashEscaped){
				if(!empty($carg)){
					$args[] = $carg;
					$carg = '';
				}
				$skip = true;
			}
			
			if(!$skip){
				if($slashEscaped) $slashEscaped = false;
				$carg .= $c;
			}
			
		}
		
		if($escaped || $slashEscaped){
			throw new \Exception('invalid arguments');
		}
		
		return $args;
	}
	
	public function close(){
		global $streams, $verbose;
		if( $this->isOpened && @fclose($this->stream) ){
			$this->isOpened = false;
			$this->stream = null;
			$streams->remove($this);
			if($verbose) uecho("client {$this->id} disconnected");
		}
		return !$this->isOpened;
	}
	
	public function isOpened(){
		return $this->isOpened;
	}
	
	public function success($result = null){
		$this->write(json_encode(array(
			'ok' => 1,
			'result' => $result
		), JSON_PRETTY_PRINT).PHP_EOL);
		$this->write(">");
	}
	
	public function error($error = null){
		$this->write(json_encode(array(
			'ok' => 0,
			'error' => is_string($error) ? $error : ($error instanceof \Exception ? $error->getMessage() : 'unknown')
		), JSON_PRETTY_PRINT).PHP_EOL);
		$this->write(">");
	}
};
