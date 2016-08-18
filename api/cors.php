<?php


class CorsMiddleware extends \Slim\Middleware
{
    public function call()
    {
        // Get reference to application
        $app = $this->app;

        if(!$app->request->isOptions()) {
            // Run inner middleware and application
            $this->next->call();
        }

        $app->response->headers->set('Access-Control-Allow-Origin', '*');
        $app->response->headers->set('Access-Control-Allow-Methods', 'PUT, GET, POST, PATCH, DELETE, HEAD');
        $app->response->headers->set('Access-Control-Allow-Headers', 'Origin, Content-Type, Accept, X-ACCESS-TOKEN, X-API-KEY, X-AUTH');
		
    }
}
