<?php
	
namespace Ething;
	

	
class Daemon
{
	
	protected $ething;
	
	public function __construct(Ething $ething) // Constructeur
	{
		$this->ething = $ething;
	}
	
	public function exec($command, Stream &$stream = null, $options = array()){
		if(!isset($stream))
			$stream = new StreamBuffer();
		
		$stream->contentType('text/plain');
		
		$daemonSettings = $this->ething->config('daemon');
		
		if(!empty($daemonSettings) && isset($daemonSettings['host']) && isset($daemonSettings['port'])){
			
			$options = array_merge(array(
				'timeout' => isset($daemonSettings['timeout']) ? $daemonSettings['timeout'] : 5,
				'interactive' => true // if false => do not wait for a response !
			), $options);
			
			$address = "tcp://".$daemonSettings['host'].":".$daemonSettings['port'];
			
			$fp = @stream_socket_client($address, $errno, $errstr, 5);
			if (!$fp) {
				$this->ething->logger()->error("unable to communicate with the daemon process {$address} ({$errno} - {$errstr})");
				$stream->errCode(2);
				$stream->out("unable to communicate with the daemon process {$address} ({$errno} - {$errstr})", Stream::STDERR);
			} else {
				
				if($options['interactive']){
					stream_set_timeout ($fp, $options['timeout']);
					
					// wait for the initialization done
					while(strlen($c = fread($fp,1))) {
						if($c === '>') break;
					}
					
					if(strlen($c)){
						
						@fwrite($fp, "{$command}\n");
						
						$out = '';
						$nl = false;
						while(strlen($c = fread($fp,1))) {
							if($c === '>' && $nl) break;
							$nl = $c === "\n";
							$out.=$c;
						}
						
						if(strlen($c)){
							$res = json_decode($out);
							if(json_last_error() === JSON_ERROR_NONE){
								if($res->ok){
									$stream->errCode(0);
									if(isset($res->result)) $stream->out($res->result);
								} else {
									$stream->errCode(1);
									$stream->out($res->error, Stream::STDERR);
								}
							}
							else {
								$stream->errCode(1);
								$stream->out('bad response', Stream::STDERR);
							}
							
						} else {
							$stream->errCode(1);
							$stream->out('timeout', Stream::STDERR);
						}
						
					
					} else {
						$stream->errCode(1);
						$stream->out('timeout', Stream::STDERR);
					}
				} else {
					@fwrite($fp, "{$command}\n");
				}
				
				$stream->close();
				
				@fclose($fp);
				
			}
		
		} else {
			$this->ething->logger()->error("bad daemon config");
			$stream->errCode(3);
			$stream->out("bad daemon config", Stream::STDERR);
		}
		
		return $stream->errCode() === 0;
	}
	
	public function restart(){
		$this->exec("restart\n");
	}
	

}


