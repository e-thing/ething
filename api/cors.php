<?php


class CorsMiddleware extends \Slim\Middleware
{
    public function call()
    {
        // Get reference to application
        $app = $this->app;
		$request = $app->request;
		$response = $app->response;
		$corsPrefightRequest = $request->isOptions() && $request->headers->get('Access-Control-Request-Method');
		
		if(!$corsPrefightRequest){
			
			// Run inner middleware and application
            $this->next->call();
			
		} else {
			$response->headers->set('Access-Control-Allow-Methods', 'PUT, GET, POST, PATCH, DELETE, HEAD');
			$response->headers->set('Access-Control-Allow-Headers', 'Origin, Content-Type, Accept, Authorization, X-API-KEY, X-AUTH, X-HTTP-Method-Override');
			$response->headers->set('Access-Control-Max-Age', '300');
		}
		
		$response->headers->set('Access-Control-Allow-Origin', '*');
		
		
    }
}
