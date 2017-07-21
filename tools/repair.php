<?php


set_time_limit(0);

ob_implicit_flush();
if(ob_get_level()) ob_end_flush();


$rootDir = __DIR__.'/..';

require_once $rootDir.'/vendor/autoload.php';
require_once $rootDir.'/src/Ething.php';
require_once $rootDir.'/session/session.php';

if(!(php_sapi_name() === 'cli' || \Session\isAuthenticated())){
	http_response_code(401);
	exit(1);
}

$eol = (php_sapi_name() === 'cli') ? PHP_EOL : '<br>';

$ething = new \Ething\Ething();

foreach ( $ething->find() as $resource ) {
	
	if(method_exists($resource, "repair")){
		
		echo "Repairing {$resource->type()} {$resource->name()} [{$resource->id()}] ... ";
		
		flush();
		
		
		try {
			$resource->repair();
			echo "ok";
		} catch( \Exception $e ) {
			echo "FAIL ({$e->getMessage()})";
		}
		
		echo $eol ;
		
		flush();
		
	}
}


echo $eol."Done".$eol;
