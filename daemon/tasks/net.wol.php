<?php


include __DIR__.'/../../src/Net.php';

use Ething\Net;


function usage(){
	echo "usage: ".basename(__FILE__, '.php')." ( --mac [mac] | --ip [ip] )".PHP_EOL;
}

$options = getopt('', array("mac:", "ip:"));



if($options){
	
	$mac = isset($options['mac']) ? $options['mac'] : null;
	$ip = isset($options['ip']) ? $options['ip'] : null;
	
	if(!$mac && $ip){
		
		if(!Net::isLocalIp($ip)){
			echo "not a local ip {$ip}".PHP_EOL;
			exit(1);
		}
		
		echo "Get mac address from ip {$ip}".PHP_EOL;
		$mac = Net::localIpToMac($ip);
		
		if(!$mac){
			echo "unable to find the mac address for the ip : {$ip}".PHP_EOL;
			exit(1);
		}
		
	}
	
	if($mac){
		echo "Send WOL packet with mac address {$mac}".PHP_EOL;
		Net::wakeOnLan($mac);
		exit(0);
	} else {
		usage();
		exit(1);
	}
	
} else {
	usage();
	exit(1);
}

