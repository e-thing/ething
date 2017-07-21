<?php

$rootDir = __DIR__.'/..';

require_once $rootDir.'/session/session.php';


if(!(php_sapi_name() === 'cli' || \Session\isAuthenticated())){
	http_response_code(401);
	exit(1);
}


header('Content-Type: application/json');

passthru("python ".$rootDir.'/src/python/serial_ports_list.py');

