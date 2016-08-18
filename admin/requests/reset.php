<?php


require_once __DIR__.'/inc.php';


try {
	$ething = ething_instanciate();
	$ething->db()->drop();
}
catch(Exception $e){
	error($e);
}






