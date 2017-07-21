<?php


/*
* Session endpoints
*/


include __DIR__.'/session.php';


$rootDir = __DIR__.'/..';


$app = new \Slim\Slim(array(
    'debug' => true
));



/*
* Routes
*/


$app->get('/login',
    function () use ($app) {

		$redirect_uri = $app->request->get('redirect_uri');
		
		if(empty($redirect_uri))
			$redirect_uri = $app->request->getRootUri() . '/..';
		
		// check if the user is not already logged in
		if(\Session\isAuthenticated()){
			
			// the user is already logged !
			// just redirect it immediately
			$app->redirect($redirect_uri);
			
			return;
			
		} else {
			
			// the user will be asked for its credentials
			$app->render('login.php', array(
				'redirect_uri' => $redirect_uri
			));
			
		}
		
    }
);

$app->get('/logout',
    function () use ($app) {
		
		\Session\unauthenticate();
		
		$redirect_uri = $app->request->get('redirect_uri');
		$loginUrl = $app->request->getRootUri() . '/login';
		
		if(!empty($redirect_uri))
			$loginUrl .= '?redirect_uri='.urlencode($redirect_uri);
		
		// redirect to the login page
		$app->redirect($loginUrl);
		
    }
);

$app->get('/status',
    function () use ($app) {
		
		$session = \Session\isAuthenticated();
		
		$app->contentType('text/plain');
		
		echo $session ? "authenticated" : "not authenticated";
		
    }
);


$app->post('/password',
    function () use ($app,$rootDir) {
		
		$req = $app->request;
		
		$password = $req->post('password');
		$redirect_uri = $req->post('redirect_uri');
		
		if(!empty($password)){
			
			if( \Session\authenticate($password) ){
				
				$app->redirect($redirect_uri);
			}
        }
		
		$app->halt(400, 'invalid authentication credentials !');
		
    }
);




$app->run();



