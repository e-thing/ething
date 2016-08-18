<?php


class CacheMiddleware extends \Slim\Middleware
{
    public function call()
    {

        $this->next->call();
		
		$response = $this->app->response;
		
		// no cache (except if it was explicitly set)
		if(!$response->headers->get('Expires'))
			$response->headers->set('Expires', 'Tue, 01 Jan 1980 1:00:00 GMT');
		
		// close the connection
		$response->headers->set('Connection', 'close');
		$response->headers->set('Content-Length', $response->getLength());
		
    }
}
