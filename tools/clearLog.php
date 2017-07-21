<?php

$rootDir = __DIR__.'/..';

require_once $rootDir.'/vendor/autoload.php';
require_once $rootDir.'/src/Ething.php';
require_once $rootDir.'/session/session.php';

if(!(php_sapi_name() === 'cli' || \Session\isAuthenticated())){
	http_response_code(401);
	exit(1);
}

$ething = new \Ething\Ething();
		

$log = $ething->config('log');

if(is_string($log)){
	file_put_contents($log, '');
}

