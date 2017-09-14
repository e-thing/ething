<?php
	
namespace Ething;
	

	
	
class Net
{
	// cf: http://www.php.net/manual/en/function.socket-create.php
	static public function ping( $host , $timeout = 1 ){
		$result = false;
		
		/* ICMP ping packet with a pre-calculated checksum */
		$package = "\x08\x00\x7d\x4b\x00\x00\x00\x00PingHost";
		/* create the socket, the last '1' denotes ICMP */
		if($socket  = @socket_create(AF_INET, SOCK_RAW, 1)){
			/* set socket receive timeout to 1 second */
			socket_set_option($socket, SOL_SOCKET, SO_RCVTIMEO, array('sec' => $timeout, 'usec' => 0));
			
			/* connect to socket */
			if(@socket_connect($socket, $host, null)){
				$ts = microtime(true);
				if (@socket_send($socket, $package, strLen($package), 0) && @socket_read($socket, 255))
					$result = microtime(true) - $ts;
			}
			
			socket_close($socket);
		}
		else{
			$e = new Exception(socket_strerror(socket_last_error()));
			throw $e;
		}

		return $result;
	}
	
	

}


