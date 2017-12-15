<?php



class Server extends Stream {
	
	protected $started = false;
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
		$stream = stream_socket_server($serverAddress, $errno, $errstr);
		if(!$stream){
			Log::error("unable to start server at {$serverAddress} , reason is {$errstr}");
			$this->started = false;
			return false;
		}
		$this->registerStream($stream, 0);
		$this->started = true;
		return true;
	}
	
	
	public function close(){
		if($this->started){
			Log::info("stop server");
			$this->closeAndUnregisterAll();
		}
	}
	
	
	public function process($stream, $id){
		
		// incomming client
		$sock = @stream_socket_accept($stream);
		$client = new Client($sock, $this->cli);
		Log::debug("new client {$client->id} connected");
		
	}
	
};
