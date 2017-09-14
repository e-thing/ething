<?php



namespace Ething\Yeelight;


class Yeelight {
	
	
	
	/*
	scan Yeelight devices on the local network
	returns :
	array(1) {
	  [0]=>
	  array(13) {
		["ip"]=>
		string(11) "192.168.1.2"
		["Cache-Control"]=>
		string(12) "max-age=3600"
		["Location"]=>
		string(28) "yeelight://192.168.1.2:55443"
		["id"]=>
		int(56763690)
		["model"]=>
		string(5) "color"
		["fw_ver"]=>
		int(52)
		["power"]=>
		string(3) "off"
		["bright"]=>
		int(100)
		["color_mode"]=>
		int(2)
		["ct"]=>
		int(2420)
		["rgb"]=>
		int(15512576)
		["hue"]=>
		int(0)
		["sat"]=>
		int(100)
	  }
	}
	*/
	static public function scan(){
		
		$bulbs = array();
		$package = "M-SEARCH * HTTP/1.1\r\nST:wifi_bulb\r\nMAN:\"ssdp:discover\"\r\n";
		
		
		if($socket  = socket_create(AF_INET, SOCK_DGRAM, 0)){
			socket_set_option($socket, SOL_SOCKET, SO_RCVTIMEO, array('sec' => 2, 'usec' => 0));
			socket_set_option($socket, SOL_SOCKET, IP_MULTICAST_TTL, 32);
			
			if(socket_sendto($socket, $package, strlen($package), 0, "239.255.255.250", 1982)){
				
				while(true){
					if(socket_recvfrom($socket, $buf, 512, 0, $remote_ip, $remote_port) === false) break;
					
					if(substr( $buf, 0, 15 ) === "HTTP/1.1 200 OK"){
						
						$bulb = array(
							'ip' => $remote_ip
						);
						
						foreach(explode("\r\n", $buf) as $line){
							
							if(preg_match('/^([^:]+):\s*(.+)\s*$/', $line, $matches)){
								$bulb[$matches[1]] = is_numeric($matches[2]) ? ($matches[2]+0) : $matches[2];
							}
							
						}
						
						$bulbs[$remote_ip] = $bulb;
						
					}
					
				}
			}
			
			socket_close($socket);
			
		} else {
			$e = new Exception(socket_strerror(socket_last_error()));
			throw $e;
		}
		
		return array_values($bulbs);
	}
	
	
	
};


