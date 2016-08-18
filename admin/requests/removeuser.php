<?php


require_once __DIR__.'/inc.php';



if( !empty($_POST) &&
	!empty($_POST['id'])
){
	
	try {
		
		$ething = ething_instanciate();
		
		$user = $ething->findOneUserById($_POST['id']);
		if(!$user)
			throw new Exception('unknown user');
		
		$user->remove();
		
	}
	catch(Exception $e){
		error($e);
	}
	
	
}
else
	error(new Exception('Bad Request'));
	

