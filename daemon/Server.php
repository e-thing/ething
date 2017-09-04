<?php



class Server extends Stream {
	
	protected $stream = null;
	protected $port;
	
	public function __construct(CommandInterpreter $cli, $port = null){
		$this->port = isset($port) ? $port : 24934;
		$this->cli = $cli;
	}
	
	public function getPort(){
		return $this->port;
	}
	
	public function start(){
		
		$serverAddress = "tcp://0.0.0.0:{$this->port}";
		Log::info("start server {$serverAddress}");
		$this->stream = stream_socket_server($serverAddress, $errno, $errstr);
		if(!$this->stream){
			Log::error("unable to start server at {$serverAddress} , reason is {$errstr}");
			$this->stream = null;
			return false;
		}
		return true;
	}
	
	
	public function close(){
		if($this->stream){
			Log::info("stop server");
			@fclose($this->stream);
			$this->stream = null;
		}
	}
	
	public function getStream(){
		return $this->stream;
	}
	
	public function process(){
		
		// incomming client
		$sock = @stream_socket_accept($this->stream);
		$client = new Client($sock, $this->cli);
		Log::debug("new client {$client->id} connected");
		
	}
	
};
