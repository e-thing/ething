<?php


include __DIR__.'/../../src/Net.php';

use Ething\Net;


function usage(){
	echo "usage: ".basename(__FILE__, '.php')." --host [host]".PHP_EOL;
}

$options = getopt('', array("host:"));


if($options && isset($options['host'])){
	
	$host = $options['host'];
	
	$result = Net::ping($host);
	
	if($result===false){
		exit(1);
	} else {
		echo $result.PHP_EOL;
		exit(0);
	}
	
} else {
	usage();
	exit(1);
}

