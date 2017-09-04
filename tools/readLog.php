<?php

$rootDir = __DIR__.'/..';

require_once $rootDir.'/vendor/autoload.php';
require_once $rootDir.'/src/Ething.php';
require_once $rootDir.'/session/session.php';

if(!(php_sapi_name() === 'cli' || \Session\isAuthenticated())){
	http_response_code(401);
	exit(1);
}

$maxLine = 0;


if(php_sapi_name() !== 'cli'){
	if(isset($_GET['line'])) $maxLine = intval($_GET['line']);
}



$ething = new \Ething\Ething();

header('Content-Type:text/plain');
echo implode("\n", $ething->logger()->read($maxLine));



