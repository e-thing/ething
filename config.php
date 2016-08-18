<?php

/**
 * @author Adrien Mezerette <a.mezerette@gmail.com>
 * @version 0.1.0
 * @package ething
 */

return array(

	// mongoDB server
    'server' => array(
		'host' => 'localhost',
		'port' => 27017,
		'user' => null,
		'password' => null,
		'database' => "ething"
    ),
	
	// credentials to access to the admin page
    'admin' => array(
        'user' => 'admin',
        'password' => 'admin',
        'onlyLocal' => false // if set to true, only local ip are allowed to connect to the admin interface
    ),
	
	// debug information is given in the error messages send through HTTP requests
	'debug' => true,
	
	// log file. Set to false to disable logging.
	'log' => __DIR__.'/debug.log',
	
	// mail (set to false to disable this feature)
	'mail' => false,
	/*'mail' = array(
        'host'=> 'smtp.gmail.com',
        'port' => 587,
        'user' => '<username>@gmail.com',
        'password' => '<password>'
    ),*/
	
	// enable Cross-origin resource sharing (CORS)
	'cors' => true,
	
	'jwt' => array(
		'secret' => 'taupesecretstring',
		'expiration' => 86400 // in seconds, the time after which the token is expired
	),
	
	// if your server is behind a proxy, set-up the proxy here
	'proxy' => false
	/*'proxy' => array(
        'host'=> '<host>',
        'port' => <port>,
        'user' => null,
        'password' => null
    )*/
	
);

