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
			socket_set_option($socket, SOL_SOCKET, SO_RCVTIMEO, array('sec' => $timeout, 'usec' => ($timeout - floor($timeout))*1000000));
			
			/* connect to socket */
			if(@socket_connect($socket, $host, null)){
				$ts = microtime(true);
				if (@socket_send($socket, $package, strLen($package), 0) && @socket_read($socket, 255))
					$result = microtime(true) - $ts;
			}
			
			socket_close($socket);
		}
		else{
			$e = new \Exception(socket_strerror(socket_last_error()));
			throw $e;
		}

		return $result;
	}
	
	static public function scanLocalNetwork(){
		
		$ips = array();
		$arpCache = Net::readArpCache();
		
		for($i=1; $i<255; $i++){
			$ip = '192.168.1.'.$i;
			$r = Net::ping($ip, 0.01);
			if($r !== false){
				
				// find the mac address
				$mac = null;
				foreach($arpCache as $item){
					if($item['ip'] === $ip){
						$mac = $item['mac'];
						break;
					}
				}
				
				$ips[] = array(
					'ip' => $ip,
					'mac' => $mac,
					'ping' => $r
				);
			}
		}
		
		return $ips;
	}
	
	static public function readArpCache(){
		
		$results = array();
		
		exec('arp -a', $lines, $returnVar);
		
		if($returnVar===0){
			foreach($lines as $line){
				if(preg_match('/\(([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3})\) at ([0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2})/', $line, $matches)){
					$ip = $matches[1];
					$mac = $matches[2];
					$results[] = array(
						'ip' => $ip,
						'mac' => $mac
					);
				}
			}
			
		}
		
		return $results;
	}
	
	// return mac address as de:ad:be:da:ae:aa
	static public function localIpToMac($localIp){
		exec('arp -a '.$localIp, $lines, $returnVar);
		
		if($returnVar===0 && count($lines)===1){
			if(preg_match('/\(([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3})\) at ([0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2})/', $lines[0], $matches)){
				$mac = $matches[2];
				return $mac;
			}
		}
		
		return null;
	}
	
	static public function wakeOnLan($macAddressHexadecimal, $broadcastAddress = null)
    {
		if(!isset($broadcastAddress)) $broadcastAddress = "192.168.1.255";
		
        $macAddressHexadecimal = str_replace(':', '', $macAddressHexadecimal);
        // check if $macAddress is a valid mac address
        if (!ctype_xdigit($macAddressHexadecimal)) {
            throw new \Exception('Mac address invalid, only 0-9 and a-f are allowed');
        }
        $macAddressBinary = pack('H12', $macAddressHexadecimal);
        $magicPacket = str_repeat(chr(0xff), 6).str_repeat($macAddressBinary, 16);
        if (!$fp = fsockopen('udp://' . $broadcastAddress, 7, $errno, $errstr, 2)) {
            throw new \Exception("Cannot open UDP socket: {$errstr}", $errno);
        }
        fputs($fp, $magicPacket);
        fclose($fp);
    }
	
	static public function isLocalIp($ip) {
		if($ip==='localhost') return true;
		
		$pri_addrs = array (
						  '10.0.0.0|10.255.255.255', // single class A network
						  '172.16.0.0|172.31.255.255', // 16 contiguous class B network
						  '192.168.0.0|192.168.255.255', // 256 contiguous class C network
						  '169.254.0.0|169.254.255.255', // Link-local address also refered to as Automatic Private IP Addressing
						  '127.0.0.0|127.255.255.255' // localhost
						 );

		$long_ip = \ip2long ($ip);
		if ($long_ip != -1 && $long_ip !== FALSE) {

			foreach ($pri_addrs AS $pri_addr) {
				list ($start, $end) = explode('|', $pri_addr);

				 // IF IS PRIVATE
				 if ($long_ip >= ip2long ($start) && $long_ip <= ip2long ($end)) {
					 return true;
				 }
			}
		}

		return false;
	}
	
	static public function isLocalhost($host) {
		return in_array($host, array("127.0.0.1","::1",'localhost'));
	}
	
	static public function hostToIp($host){
		exec('host '.$host, $lines, $returnVar);
		
		if($returnVar===0 && count($lines)>0){
			if(preg_match('/ has address ([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3})/', $lines[0], $matches)){
				$ip = $matches[1];
				return $ip;
			}
		}
		
		return null;
	}
	
}


