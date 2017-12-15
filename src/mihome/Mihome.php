<?php



namespace Ething\Mihome;


class Mihome {
	
	const MULTICAST_ADDRESS = '224.0.0.50';
    const MULTICAST_PORT    = 9898;
    const SERVER_PORT       = 4321;
    const SOCKET_BUFSIZE    = 1024;
	
	const IV = "\x17\x99\x6d\x09\x3d\x28\xdd\xb3\xba\x69\x5a\x2e\x6f\x58\x56\x2e";
	
	
	static public function scan(){
		
		$gateways = array();
		
		$message = '{"cmd":"whois"}';
		
		if($socket = socket_create(AF_INET, SOCK_DGRAM, 0)){
			socket_set_option($socket, SOL_SOCKET, SO_BROADCAST, true);
			socket_set_option($socket, SOL_SOCKET, SO_RCVTIMEO, array('sec' => 5, 'usec' => '0'));
			
			if(socket_sendto($socket, $message, strlen($message), 0, Mihome::MULTICAST_ADDRESS, Mihome::SERVER_PORT)){
				
				while(true){
					if(socket_recvfrom($socket, $buf, Mihome::SOCKET_BUFSIZE, 0, $remote_ip, $remote_port) === false) break;
					
					$response = \json_decode($buf, true);
					if(is_array($response)){
						if($response['cmd'] === 'iam' && $response['model'] === 'gateway'){
							
							$gateway = array(
								'port' => intval($response['port']),
								'sid' => $response['sid'],
								'model' => $response['model']
							);
							
							$gateways[$remote_ip] = $gateway;
						}
					}
					
				}
					
			}
			
			socket_close($socket);
		}
		
        return array_values($gateways);
	}
	
	
	
};


