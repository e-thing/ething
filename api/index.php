<?php

/**
 * @swagger
 * {  
 *      "swagger": "2.0",
 *      "paths": [],
 *      "info": {
 *         "title": "eThing HTTP api",
 *         "description": "
 
The eThing project is an 'Internet of Things' application. Store and retrieve data from devices using HTTP requests.

Access to your resources (file, table, device ...) through HTTP requests.

-------------


### Resource description

There are different types of resources. A resource can either be :

 - file : use this kind of objects to store text data or binary data (image, ...)
 - table : tables are used to store a collection of related data. Table consists of fields and rows.
 - device : this resource describes a device. You can send HTTP requests to your device through it.
 - app : this resource is used to store a HTML/JavaScript script. Use it to handle your data (for instance, you can create an interface to communicate with your device).


### Error messages

When the API returns error messages, it does so in JSON format. For example, an error might look like this:

```json
{
  \"message\": \"The resource does not exist\",
  \"code\" : 404
}
```

The code value correspond to the HTTP status code of the response.


### Authorization

Currently you can authenticate via an API Key or via an Access Token (acquired using regular login (see /user/login endpoint) ).

#### API key

You can generate an API key by creating a new device. Then the API key will be listed on developer page [http://<YOUR_SERVER_ADDRESS>/ething/client/developer.html](http://localhost/ething/client/developer.html).

Send the following header below on every request :

```
X-API-KEY: <YOUR_API_KEY>
```

Here is a cURL example of how to send this header :

```bash
curl -H 'X-API-KEY: <YOUR_API_KEY>' ...
```

You can also simply pass the key as a URL query parameter when making Web service requests. For example:

```bash
curl http://localhost/ething/api/resources?api_key=<YOUR_API_KEY>
```

### Partial response

By default, the server sends back the full representation of a resource after processing requests.
For better performance, you can ask the server to send only the fields you really need and get a partial response instead.

To request a partial response, use the fields request parameter to specify the fields you want returned.
You can use this parameter with any request that returns response data.

example:

This request will return the meta-data representation containing only the specified keys of a resource

`/resource/56731_a?fields=id,name`


### Filter resource or table data

You can search or filter resources or table's rows using a search query combining one or more search clauses. Each search clause is made up of three parts.

 - Field : in case of resource filtering, it corresponds to the attribute of the resource that is searched (e.g. 'name'). In case of table's rows filtering, it corresponds to the column's name.
 - Operator : test that is performed on the data to provide a match.
 - Value : The content of the field that is tested.
 
Combine clauses with the conjunctions and or or.


The available fields for resource filtering (see the HTTP API documentation for their meaning) :

 - 'type'
 - 'name'
 - 'mime'
 - 'id'
 - 'location.latitude'
 - 'location.longitude'
 - 'location.altitude'
 - 'createdDate'
 - 'modifiedDate'
 - 'createdBy.type'
 - 'createdBy.id'
 - 'description'
 - 'length' : only available for Table resources
 - 'size' : only available for File resources
 - 'hasThumbnail' : only available for File resources
 - 'hasIcon' : only available for App resources
 - 'battery' : only available for Device resources
 - 'lastSeenDate' : only available for Device resources


The available operators :

 - '==' : equal to ... This operator is compatible with any types of value.
 - '!=' : not equal to ... This operator is compatible with any types of value.
 - 'is' : is of type ... This operator is compatible with any types of value.
 - '>' : greater than ... This operator is only compatible with numbers or dates.
 - '<' : less than ... This operator is only compatible with numbers or dates.
 - '>=' : greater than or equal to ... This operator is only compatible with numbers.
 - '<=' : less than or equal to ... This operator is only compatible with numbers.
 - '^=' : start with ... This operator is only compatible with strings.
 - '$=' : end with ... This operator is only compatible with strings.
 - '*=' : contain ... This operator is only compatible with strings.
 - '~=' : contain the word ... This operator is only compatible with strings.
 
 
Value types :

 - String : surround with single quotes ' or double quotes.
 - Number : either integer numbers or floating numbers.
 - Boolean : true or false.
 - Date : *RFC 3339* format,  e.g., *2015-03-24T12:00:00+02:00*.


Examples:

All examples on this page show the unencoded q parameter, where name == 'foobar' is encoded as name+%3d%3d+%27foobar%27.
Client libraries handle this encoding automatically.

Search for resources with the name \"foobar\"

`name == 'foobar'`

Search for plain text files

`mime == 'text/plain'`

Search for tables resources only

`type == 'Table'`

Search for non empty files or tables

`size > 0 OR length > 0`

Search for resources with the name starting with \"foo\"

`name ^= 'foobar'`

Search for tables with the extension 'db' or files with the extension 'csv'

`( type == 'Table' AND name $= '.db' ) OR ( type == 'File' AND name $= '.csv' )`

Search for resources modified after Mars 4th 2016

`modifiedDate > '2016-03-04T00:00:00+01:00'`



 ",
 *         "version": "0.1.0"
 *      },
 *      "basePath": "/ething/api",
 *      "schemes": ["http"],
 *      "consumes": ["application/json"],
 *      "produces": ["application/json"],
 *      "security":[{
 *      	"access_token": []
 *      }],
 *      "securityDefinitions":{
 *        "access_token": {
 *          "type": "apiKey",
 *          "description": "authentication through an access token, use /user/login request to generate an access token",
 *          "name": "X-ACCESS-TOKEN",
 *          "in": "header"
 *        },
 *        "api_key": {
 *          "type": "apiKey",
 *          "description": "authentication through an API key, used only by device.",
 *          "name": "X-API-KEY",
 *          "in": "header"
 *        }
 *      },
 *      "tags": [
 *      	{
 *      		"name": "auth",
 *      		"description": "Authentication endpoints."
 *      	},
 *      	{
 *      		"name": "resource",
 *      		"description": "Operations on resources no matter his type."
 *      	},
 *      	{
 *      		"name": "file",
 *      		"description": "Operations specific to File resource"
 *      	},
 *      	{
 *      		"name": "table",
 *      		"description": "Operations specific to Table resource"
 *      	},
 *      	{
 *      		"name": "app",
 *      		"description": "Operations specific to Application resource"
 *      	},
 *      	{
 *      		"name": "device",
 *      		"description": "Operations specific to Device resource"
 *      	},
 *      	{
 *      		"name": "user",
 *      		"description": "Operations to manage User"
 *      	}
 *      ]
 *   }
 */

$rootDir = __DIR__.'/..';

$config = include($rootDir.'/config.php');

require_once __DIR__.'/utils.php';

// composer
require $rootDir.'/vendor/autoload.php';

$app = new \Slim\Slim(array(
    'debug' => false
));

$debug = isset($config['debug']) && $config['debug'];

require_once $rootDir.'/src/Ething.php';
$ething = new \Ething\Ething($config);

require_once __DIR__.'/auth.php';
$auth = new \Auth\HttpAuth($ething, isset($config['jwt']) ? $config['jwt'] : array());

error_reporting($debug ? E_ALL : 0);



/*
* Routes
*/


$app->get('/swagger.json',
    function () use ($app) {
		
		$swaggerFile = __DIR__.'/Swagger/swagger.json';
		
		if(is_file($swaggerFile)){
			$app->lastModified(filemtime($swaggerFile));
			
			$app->contentType('application/json');
			readfile($swaggerFile);
		}
		else
			throw new \Utils\Exception('not found',404);
		
    }
);







/**
 * @swagger-path
 * "/auth/authorize":{  
 *      "post":{
 *         "tags": ["auth"],
 *         "security":[],
 *         "summary": "initialize a new session",
 *         "description":"The login endpoint is used to initialize a new session. A JSON web token will be generated. Use this token to make further API requests.",
 *         "parameters":[  
 *            {  
 *               "name":"credentials",
 *               "in":"body",
 *               "description":"the credentials of the user to be authenticated.
 
 example :
 
```json
{
	\"user\":\"john\",
	\"password\":\"secret\"
}
```

 ",
 *               "required":true,
 *               "schema":{
 *               	"type":"object",
 * 	                "properties":{  
 * 	                	"user":{
 * 	                	   "type":"string",
 * 	                	   "description":"the user name"
 * 	                	},
 * 	                	"password":{
 * 	                	   "type":"string",
 * 	                	   "description":"the password"
 * 	                	}
 *                  }
 *               }
 *            }
 *         ],
 *         "responses":{
 *            "200":{
 *               "description":"Successfully authenticated. The answer contains a JSON web token.",
 *               "schema":{
 *               	"type":"object",
 * 	                "properties":{  
 * 	                	"token":{
 * 	                	   "type":"string",
 * 	                	   "description":"a JSON web token."
 * 	                	}
 *                  }
 *               }
 *            },
 *            "401":{
 *               "description":"The authentication fails. Invalid credentials.",
 *               "schema":{
 *                  "$ref":"#/definitions/Error"
 *               }
 *            }
 *         }
 *      }
 *   }
 */
$app->post('/auth/authorize',
    function () use ($app,$auth,$ething) {
	
		$data = Utils\getJSON($app,true);
		
        if(is_array($data) && isset($data['user']) && isset($data['password']) && is_string($data['user']) && is_string($data['password']) && ($user = $ething->findOneUserByName($data['user'])) && $user->password() === md5($data['password']) ) {
			
			$auth->authenticate($user);
			
			// generate a new token
			$jwt = $auth->generateToken();
			
			// send back the token
			$app->contentType('application/json');
			echo json_encode(array(
				'token' => $jwt
			),JSON_PRETTY_PRINT|JSON_UNESCAPED_SLASHES);
			
        }
		else
			throw new \Utils\Exception('not authorized',401);
		
    }
);

/**
 * @swagger-path
 * "/auth/token":{
 *      "get":{
 *         "security":[{"access_token":[]}],
 *         "tags": ["auth"],
 *         "summary": "Refresh a JSON web token",
 *         "description":"Use this endpoint to refresh the expiration date of a token.

If it returns an unauthorized error (401), it means that your token has expired.
You need to login to get a new token (see /auth/authorize endpoint).

If it returns with no error, the answer contains the token with the expiration date renewed.
",
 *         "responses":{
 *            "200":{
 *               "description":"Your token is still valid.",
 *               "schema":{
 *               	"type":"object",
 * 	                "properties":{  
 * 	                	"token":{
 * 	                	   "type":"string",
 * 	                	   "description":"a JSON web token."
 * 	                	}
 *                  }
 *               }
 *            },
 *            "401":{
 *               "description":"Your token has expired.",
 *               "schema":{
 *                  "$ref":"#/definitions/Error"
 *               }
 *            }
 *         }
 *      }
 *   }
 */
$app->get('/auth/token',
    function () use ($app,$auth,$ething) {
		
		// only the 'token' mode can ask for a new token !
		if($auth->mode() !== 'token')
			throw new \Utils\Exception('Forbidden',403);
		
		// generate a new token
		$jwt = $auth->generateToken();
		
		// send back the token
		$app->contentType('application/json');
		echo json_encode(array(
			'token' => $jwt
		),JSON_PRETTY_PRINT|JSON_UNESCAPED_SLASHES);
		
    }
);


/**
 * @swagger-path
 * "/profile":{  
 *      "get":{
 *         "tags": ["user"],
 *         "security":[{"access_token":[]}],
 *         "description":"Returns the profile of the authenticated user.",
 *         "responses":{
 *            "200":{
 *               "description":"The user profile",
 *               "schema":{
 *               	"$ref":"#/definitions/Profile"
 *               }
 *            }
 *         }
 *      }
 *   }
 */
$app->get('/profile',
    function () use ($app,$auth,$ething) {
		$app->contentType('application/json');
		echo json_encode($auth->user()->profile(),JSON_PRETTY_PRINT|JSON_UNESCAPED_SLASHES);
		
    }
);

/**
 * @swagger-path
 * "/profile":{  
 *      "patch":{
 *         "tags": ["user"],
 *         "security":[{"access_token":[]}],
 *         "description":"update information about the authenticated user. Use this endpoint if you want to change your mail or any other information about your profile (except for your username).",
 *         "parameters":[  
 *            {  
 *               "name":"data",
 *               "in":"body",
 *               "description":"the attributes to modify",
 *               "required":true,
 *               "schema":{
 *                  "$ref":"#/definitions/Profile"
 *               }
 *            }
 *         ],
 *         "responses":{
 *            "200":{
 *               "description":"user successfully updated",
 *               "schema":{
 *                  "$ref":"#/definitions/Profile"
 *               }
 *            },
 *            "400":{
 *               "description":"an error occurs",
 *               "schema":{
 *                  "$ref":"#/definitions/Error"
 *               }
 *            }
 *         }
 *      }
 *   }
 */
$app->patch('/profile',
    function () use ($app,$auth,$ething) {
		if($auth->user()->set((array)Utils\getJSON($app))){
			$app->contentType('application/json');
			echo json_encode($auth->user()->profile(),JSON_PRETTY_PRINT|JSON_UNESCAPED_SLASHES);
		}
		else {
			throw new \Utils\Exception('Invalid request');
		}
    }
);





/**
 * @swagger-path
 * "/resources":{  
 *      "get":{
 *         "tags": ["resource"],
 *         "security":[{"access_token":[]}],
 *         "summary":"Lists the user's resources.",
 *         "description":"
Lists the user's resources.

#### cURL example

```bash
curl -H 'X-API-KEY: <YOUR_API_KEY>' http://localhost/ething/api/resources
```

",
 *         "parameters":[  
 *            {  
 *               "name":"q",
 *               "in":"query",
 *               "description":"Query string for searching resources",
 *               "required":false,
 *               "type":"string"
 *            },
 *            {  
 *               "name":"limit",
 *               "in":"query",
 *               "description":"Limits the number of resources returned",
 *               "required":false,
 *               "type":"integer",
 *               "minimum":0
 *            },
 *            {  
 *               "name":"skip",
 *               "in":"query",
 *               "description":"Skips a number of resources",
 *               "required":false,
 *               "type":"integer",
 *               "minimum":0
 *            },
 *            {  
 *               "name":"sort",
 *               "in":"query",
 *               "description":"The key on which to do the sorting, by default the sort is made by modifiedDate descending. To make the sort descending, prepend the field name by minus '-'. For instance, '-createdDate' will sort by createdDate descending ",
 *               "required":false,
 *               "type":"string"
 *            }
 *         ],
 *         "responses":{
 *            "200":{
 *               "description":"A list of resources",
 *               "schema":{
 *                  "type":"array",
 *                  "items":{  
 *                     "$ref":"#/definitions/Resource"
 *                  }
 *               }
 *            }
 *         }
 *      }
 *   }
 */

$app->get('/resources',
    function () use ($app,$auth,$ething) {
		$app->contentType('application/json');
		echo Utils\jsonEncodeFilterByFields($auth->fs()->all(
			Utils\getParameter('q',Utils\CHK_STRING, true, null),
			Utils\getParameter('limit',Utils\CHK_UNSIGNED_INT, true, null),
			Utils\getParameter('skip',Utils\CHK_UNSIGNED_INT, true, null),
			Utils\getParameter('sort',Utils\CHK_STRING,true,null)
		),Utils\getParameter('fields',Utils\CHK_STRING_ARRAY, true, null));
    }
);

/**
 * @swagger-path
 * "/usage":{  
 *      "get":{
 *         "tags": ["resource"],
 *         "security":[{"access_token":[]}],
 *         "description":"Returns information about the resource usage",
 *         "responses":{
 *            "200":{
 *               "description": "Some usage information",
 *               "schema":{
 *                  "type":"object",
 * 	                "properties":{  
 * 	                	"used":{  
 * 	                	   "type":"number",
 * 	                	   "description":"The space used in bytes"
 * 	                	},
 * 	                	"quota_size":{  
 * 	                	   "type":"number",
 * 	                	   "description":"The maximum space authorized in bytes"
 * 	                	}
 *                  }
 *               },
 *               "examples":{
 *               	"application/json": {
 *                     "quota_size":100000000,
 *                     "used":697699
 *               	}
 *               }
 *            }
 *         }
 *      }
 *   }
 */
$app->get('/usage',
    function () use ($app,$auth,$ething) {
		$app->contentType('application/json');
		echo json_encode($auth->fs()->stats(),JSON_PRETTY_PRINT|JSON_UNESCAPED_SLASHES);
    }
);



/**
 * @swagger-path
 * "/resources/{id}":{  
 *      "get":{
 *         "tags": ["resource"],
 *         "security":[{"access_token":[]}],
 *         "summary":"Gets the meta-data of a resource.",
 *         "description":"
 Returns the meta-data of a resource in JSON.
 ",
 *         "parameters":[  
 *            {  
 *               "name":"id",
 *               "in":"path",
 *               "description":"id of the resource",
 *               "required":true,
 *               "type":"string"
 *            }
 *         ],
 *         "responses":{
 *            "200":{
 *               "description":"resource object",
 *               "schema":{
 *                  "$ref":"#/definitions/Resource"
 *               },
 *               "examples":{
 *               	"application/json": {
 *                    "name":"myfile.txt",
 *                    "data":null,
 *                    "description":null,
 *                    "expireAfter":null,
 *                    "user":{
 *                  	 "id":"56731_a",
 *                  	 "name":"john"
 *                    },
 *                    "type":"File",
 *                    "createdBy":{
 *                  	 "id":"56a7B-5",
 *                  	 "type":"Device"
 *                    },
 *                    "createdDate":"2016-01-27T07:46:43+00:00",
 *                    "modifiedDate":"2016-02-13T10:34:31+00:00",
 *                    "mime":"text\/plain",
 *                    "size":251,
 *                    "rules":[],
 *                    "loc":null,
 *                    "id":"1b7-_37",
 *                    "thumbnail":false
 *               	}
 *               }
 *            }
 *         }
 *      }
 *   }
 */
$app->get('/resources/:id',
    function ($id) use ($app,$auth,$ething) {
		$r = Utils\getResource($auth, $id);
		
		$app->contentType('application/json');
		echo Utils\jsonEncodeFilterByFields($r,Utils\getParameter('fields',Utils\CHK_STRING_ARRAY, true, null));
    }
);

/**
 * @swagger-path
 * "/resources/{id}":{  
 *      "delete":{
 *         "tags": ["resource"],
 *         "security":[{"access_token":[]}],
 *         "description":"deletes a resource",
 *         "parameters":[  
 *            {  
 *               "name":"id",
 *               "in":"path",
 *               "description":"id of the resource",
 *               "required":true,
 *               "type":"string"
 *            }
 *         ],
 *         "responses":{
 *            "200":{
 *               "description":"the resource has been deleted successfully"
 *            }
 *         }
 *      }
 *   }
 */
$app->delete('/resources/:id',
    function ($id) use ($app,$auth,$ething) {
		$r = Utils\getResource($auth, $id);
		$r->remove();
    }
);

/**
 * @swagger-path
 * "/resources/{id}":{  
 *      "patch":{
 *         "tags": ["resource"],
 *         "security":[{"access_token":[]}],
 *         "description":"update a resource. Only properties which are not readonly can be modified.
 
Rename a resource :

```json
{
   \"name\":\"myFileRenamed.txt\"
}
```

Set a location for a resource :

```json
{
   \"loc\":{
      \"latitude\": 5.12,
	  \"longitude\": -45.78
   }
}
```

Clear a description :

```json
{
   \"description\":null
}
```
 ",
 *         "parameters":[  
 *            {  
 *               "name":"id",
 *               "in":"path",
 *               "description":"id of the resource",
 *               "required":true,
 *               "type":"string"
 *            },
 *            {  
 *               "name":"modification",
 *               "in":"body",
 *               "description":"the attributes to modify",
 *               "required":true,
 *               "schema":{
 *                  "$ref":"#/definitions/Resource"
 *               }
 *            }
 *         ],
 *         "responses":{
 *            "200":{
 *               "description":"resource successfully updated",
 *               "schema":{
 *                  "$ref":"#/definitions/Resource"
 *               }
 *            },
 *            "400":{
 *               "description":"an error occurs",
 *               "schema":{
 *                  "$ref":"#/definitions/Error"
 *               }
 *            }
 *         }
 *      }
 *   }
 */
$app->patch('/resources/:id',
    function ($id) use ($app,$auth,$ething) {
		$r = Utils\getResource($auth, $id);
		
		if($r->set((array)Utils\getJSON($app))){
			$app->contentType('application/json');
			echo Utils\jsonEncodeFilterByFields($r,Utils\getParameter('fields',Utils\CHK_STRING_ARRAY, true, null));
		}
		else {
			throw new \Utils\Exception('Invalid patch request');
		}
    }
);

/**
 * @swagger-path
 * "/file":{  
 *      "get":{
 *         "tags": ["file"],
 *         "security":[{"access_token":[]}],
 *         "description":"Lists the user's files",
 *         "parameters":[ 
 *            {  
 *               "name":"limit",
 *               "in":"query",
 *               "description":"Limits the number of files returned",
 *               "required":false,
 *               "type":"integer"
 *            },
 *            {  
 *               "name":"skip",
 *               "in":"query",
 *               "description":"Skips a number of files",
 *               "required":false,
 *               "type":"integer"
 *            }
 *         ],
 *         "responses":{
 *            "200":{
 *               "description":"A list of files",
 *               "schema":{
 *                  "type":"array",
 *                  "items":{  
 *                     "$ref":"#/definitions/File"
 *                  }
 *               }
 *            }
 *         }
 *      }
 *   }
 */
$app->get('/file',
    function () use ($app,$auth,$ething) {
		$app->contentType('application/json');
		echo Utils\jsonEncodeFilterByFields($auth->fs()->all(
			'type == "File"',
			Utils\getParameter('limit',Utils\CHK_UNSIGNED_INT, true, null),
			Utils\getParameter('skip',Utils\CHK_UNSIGNED_INT, true, null)
		),Utils\getParameter('fields',Utils\CHK_STRING_ARRAY, true, null));
    }
);

/**
 * @swagger-path
 * "/file":{  
 *      "post":{
 *         "tags": ["file"],
 *         "security":[{"access_token":[]}],
 *         "description":"

Creates a new file.

There are 2 ways to pass directly the content of the file on the same request :

 - pass the content as a base-64 encoded ASCII string through the key 'content' of the metadata object.
 
 example:

```json
{
   \"name\": \"myfile.txt\",
   \"content\": \"SGVsbG8gd29ybGQgIQ==\" // 'Hello world !' in base-64
}
```
 
 - multipart/related request: transfers the content along with metadata that describes it. *The metadata part must come first*.
 
 example:
 
```
POST /ething/api/file HTTP/1.1
Host: <YOUR_HOST>
Content-Type: multipart/related; boundary=foo_bar_baz

--foo_bar_baz
Content-Type: application/json; charset=UTF-8

{
  \"name\": \"image.jpg\"
}

--foo_bar_baz
Content-Type: image/jpeg

<JPEG DATA>
--foo_bar_baz--
```

#### cURL example

The next command will create a new file 'myfile.txt'.

```bash
curl
	-H 'X-API-KEY: <YOUR_API_KEY>'
	-H \"Content-Type: application/json\"
	-X POST
	-d '{\"name\":\"myfile.txt\"}'
	http://localhost/ething/api/file
```

If the command was successful, a response containing the meta data of the created file will be given back.
You will find in it the id of that file.
This id is a unique string identifying this file and is necessary to make any operation on it.

```json
{
  \"id\":\"73c66-4\",
  \"name\":\"descriptor.txt\",
  \"data\":null,
  \"description\":null,
  \"expireAfter\":null,
  \"user\":{
	 \"id\":\"56731a7\",
	 \"name\":\"john\"
  },
  \"type\":\"File\",
  \"createdBy\":null,
  \"createdDate\":\"2016-01-27T07:46:43+00:00\",
  \"modifiedDate\":\"2016-02-13T10:34:31+00:00\",
  \"mime\":\"text/plain\",
  \"size\":0,
  \"rules\":[],
  \"loc\":null,
  \"hasThumbnail\":false,
  \"isText\": true
}
```


",
 *         "parameters":[  
 *            {  
 *               "name":"metadata",
 *               "in":"body",
 *               "description":"
the metadata of the file to be created

example:

```json
{
   \"name\": \"myfile.txt\",
   \"description\": \"an optional description\"
}
```
 ",
 *               "required":true,
 *               "schema":{
 *               	"$ref":"#/definitions/File"
 *               }
 *            }
 *         ],
 *         "responses":{
 *            "200":{
 *               "description":"The file was successfully created",
 *               "schema":{
 *               	"$ref":"#/definitions/File"
 *               },
 *               "examples":{
 *               	"application/json": {
 *                    "name":"myfile.txt",
 *                    "data":null,
 *                    "description":null,
 *                    "expireAfter":null,
 *                    "user":{
 *                  	 "id":"56731_a",
 *                  	 "name":"john"
 *                    },
 *                    "type":"File",
 *                    "createdBy":{
 *                  	 "id":"56a7B-5",
 *                  	 "type":"Device"
 *                    },
 *                    "createdDate":"2016-01-27T07:46:43+00:00",
 *                    "modifiedDate":"2016-02-13T10:34:31+00:00",
 *                    "mime":"text\/plain",
 *                    "size":251,
 *                    "rules":[],
 *                    "loc":null,
 *                    "id":"1b7-_37",
 *                    "thumbnail":false
 *               	}
 *               }
 *            }
 *         }
 *      }
 *   }
 */
$app->post('/file',
    function () use ($app,$auth,$ething) {
		$multipart = Utils\readMultipartRelated();
		
		if($multipart){
			if(count($multipart)==2 && isset($multipart[0]['headers']['Content-Type']) && Utils\getMediaType($multipart[0]['headers']['Content-Type'])==='application/json'){
				$attr = json_decode($multipart[0]['body'], true);
				if(json_last_error() !== JSON_ERROR_NONE)
					throw new \Utils\Exception('Invalid JSON: '.json_last_error_msg());
				$content = $multipart[1]['body'];
			}
			else
				throw new \Utils\Exception('invalid multipart/related content');
		}
		else
			$attr = (array)Utils\getJSON($app);
		
		$r = $ething->create($auth->user(),'File',$attr,$auth->device());
		if(!$r) throw new \Utils\Exception('Unable to create the file');
		if(isset($content))
			$r->write($content);
		$app->response()->setStatus(201);
		$app->contentType('application/json');
		echo Utils\jsonEncodeFilterByFields($r,Utils\getParameter('fields',Utils\CHK_STRING_ARRAY, true, null));
		
    }
);

/**
 * @swagger-path
 * "/file/{id}":{  
 *      "get":{
 *         "tags": ["file"],
 *         "security":[{"access_token":[]}],
 *         "description":"

Retrieves the content of a file.

#### cURL example

The next command show you how to read the content of a file identified by its id.

```bash
curl -H 'X-API-KEY: <YOUR_API_KEY>' http://localhost/ething/api/file/<FILE_ID>
```

",
 *         "produces":["*\/*"],
 *         "parameters":[
 *            {  
 *               "name":"id",
 *               "in":"path",
 *               "description":"id of the resource",
 *               "required":true,
 *               "type":"string"
 *            }
 *         ],
 *         "responses":{
 *            "200":{
 *               "description":"The content of this file",
 *               "schema": {
 *               	"type":"file"
 *               }
 *            }
 *         }
 *      }
 *   }
 */
$app->get('/file/:id',
    function ($id) use ($app,$auth,$ething) {
		$r = Utils\getResource($auth, $id, 'File');
		$app->lastModified($r->modifiedDate());
		$content = $r->read();
		$app->contentType($r->mime());
		$app->response->headers->set('Content-Length', strlen($content));
		echo $content;
    }
);

/**
 * @swagger-path
 * "/file/{id}":{  
 *      "put":{
 *         "tags": ["file"],
 *         "security":[{"access_token":[]}],
 *         "description":"
Upload the content of a file.

#### cURL example

The next command show you how to send the content of the local file 'data.txt' into a file.

```bash
curl
	-H 'X-API-KEY: <YOUR_API_KEY>'
	-X PUT
	--data @data.txt
	http://localhost/ething/api/file/<FILE_ID>
```

",
 *         "consumes": ["*\/*"],
 *         "parameters":[  
 *            {  
 *               "name":"id",
 *               "in":"path",
 *               "description":"id of the resource",
 *               "required":true,
 *               "type":"string"
 *            },
 *            {  
 *               "name":"append",
 *               "in":"query",
 *               "description":"Set to true to append the new content",
 *               "required":false,
 *               "type":"boolean",
 *               "default":false
 *            },
 *            {  
 *               "name":"content",
 *               "in":"body",
 *               "description":"The new content. Could be of any type.",
 *               "required":true,
 *               "schema": {
 *               	"type": "string",
 *               	"format": "binary"
 *               }
 *            }
 *         ],
 *         "responses":{
 *            "200":{
 *               "description":"The file's metadata",
 *               "schema":{
 *                  "$ref":"#/definitions/File"
 *               }
 *            }
 *         }
 *      }
 *   }
 */
$app->put('/file/:id',
    function ($id) use ($app,$auth,$ething) {
		$r = Utils\getResource($auth, $id, 'File');
		$append = Utils\getParameter('APPEND',Utils\CHK_LOGIC,true,false);
		$bytes = $app->request->getBody();
		
		Utils\spaceControl($auth,mb_strlen($bytes, '8bit'));
		
		if(!$append)
			$r->write($bytes);
		else
			$r->append($bytes);
		
		$app->contentType('application/json');
		echo Utils\jsonEncodeFilterByFields($r,Utils\getParameter('fields',Utils\CHK_STRING_ARRAY, true, null));
		
    }
);

/**
 * @swagger-path
 * "/file/{id}/thumbnail":{  
 *      "get":{
 *         "tags": ["file"],
 *         "security":[{"access_token":[]}],
 *         "description":"Retrieves the thumbnail of a file. Only image can have a thumbnail. The thumbnail is automatically generated when the content is uploaded.",
 *         "parameters":[  
 *            {  
 *               "name":"id",
 *               "in":"path",
 *               "description":"id of the resource",
 *               "required":true,
 *               "type":"string"
 *            }
 *         ],
 *         "produces":["image/jpeg","image/png"],
 *         "responses":{
 *            "200":{
 *               "description":"The thumbnail of this image",
 *               "schema": {
 *               	"type":"file"
 *               }
 *            }
 *         }
 *      }
 *   }
 */
$app->get('/file/:id/thumbnail',
    function ($id) use ($app,$auth,$ething) {
		$r = Utils\getResource($auth, $id, 'File');
		$app->lastModified($r->modifiedDate());
		$content = $r->readThumbnail();
		if(is_null($content))
			throw new \Utils\Exception('No thumbnail available',404);
		$finfo = new finfo(FILEINFO_MIME);
		$app->contentType($finfo->buffer($content));
		echo $content;
    }
);

/**
 * @swagger-path
 * "/table":{  
 *      "get":{
 *         "tags": ["table"],
 *         "security":[{"access_token":[]}],
 *         "description":"Lists the user's tables",
 *         "parameters":[ 
 *            {  
 *               "name":"limit",
 *               "in":"query",
 *               "description":"Limits the number of tables returned",
 *               "required":false,
 *               "type":"integer"
 *            },
 *            {  
 *               "name":"skip",
 *               "in":"query",
 *               "description":"Skips a number of tables",
 *               "required":false,
 *               "type":"integer"
 *            }
 *         ],
 *         "responses":{
 *            "200":{
 *               "description":"A list of tables",
 *               "schema":{
 *                  "type":"array",
 *                  "items":{  
 *                     "$ref":"#/definitions/Table"
 *                  }
 *               }
 *            }
 *         }
 *      }
 *   }
 */
$app->get('/table',
    function () use ($app,$auth,$ething) {
		$app->contentType('application/json');
		echo Utils\jsonEncodeFilterByFields($auth->fs()->all(
			'type == "Table"',
			Utils\getParameter('limit',Utils\CHK_UNSIGNED_INT, true, null),
			Utils\getParameter('skip',Utils\CHK_UNSIGNED_INT, true, null)
		),Utils\getParameter('fields',Utils\CHK_STRING_ARRAY, true, null));
    }
);

/**
 * @swagger-path
 * "/table":{  
 *      "post":{
 *         "tags": ["table"],
 *         "security":[{"access_token":[]}],
 *         "description":"
Creates a new table.

You may want to pass directly the content of the table in the same request. To do so, just pass the data through the key 'content' of the metadata object;
 
example:

```json
{
   \"name\": \"matable.db\",
   \"content\": [
		{
			\"temperature\": 12.5,
			\"pressure\": 101325
		}
   ]
}
```

#### cURL example

The next command will create a new table 'mytable.db'.

```bash
curl
	-H 'X-API-KEY: <YOUR_API_KEY>'
	-H \"Content-Type: application/json\"
	-X POST
	-d '{\"name\":\"mytable.db\"}'
	http://localhost/ething/api/table
```

If the command was successful, a response containing the meta data of the created table will be given back.
You will find in it the id of that table.
This id is a unique string identifying this table and is necessary to make any operation on it.

```json
{
  \"id\":\"56_df0f\",
  \"name\":\"mytable.db\",
  \"data\":null,
  \"description\":null,
  \"maxLength\":null,
  \"expireAfter\":null,
  \"user\":{
	 \"id\":\"56731a7\",
	 \"name\":\"lebios\"
  },
  \"type\":\"Table\",
  \"createdBy\":{
	 \"id\":\"5Ab-32a\",
	 \"name\":\"lebios\"
  },
  \"createdDate\":\"2016-02-12T14:49:30+00:00\",
  \"modifiedDate\":\"2016-02-15T13:03:20+00:00\",
  \"mime\":\"x-table/x-table\",
  \"rules\":[],
  \"length\":421,
  \"keys\":{
	 \"temp1\":421,
	 \"temp2\":421
  },
  \"loc\":null
}
```

",
 *         "parameters":[  
 *            {  
 *               "name":"metadata",
 *               "in":"body",
 *               "description":"

The metadata of the table to be created.

example:

```json
{
	\"name\":\"mytable.db\"
}
```
 ",
 *               "required":true,
 *               "schema":{
 *               	"$ref":"#/definitions/Table"
 *               }
 *            }
 *         ],
 *         "responses":{
 *            "200":{
 *               "description":"The table was successfully created",
 *               "schema":{
 *               	"$ref":"#/definitions/Table"
 *               },
 *               "examples":{
 *               	"application/json": {
 *                     "id":"1b7-_37",
 *                     "name":"mytable.db",
 *                     "data":null,
 *                     "description":null,
 *                     "maxLength":null,
 *                     "expireAfter":null,
 *                     "user":{
 *                   	 "id":"56731_a",
 *                   	 "name":"John"
 *                     },
 *                     "type":"Table",
 *                     "createdBy":{
 *                  	 "id":"56a7B-5",
 *                  	 "type":"Device"
 *                    },
 *                     "createdDate":"2016-02-12T14:49:30+00:00",
 *                     "modifiedDate":"2016-02-15T13:03:20+00:00",
 *                     "mime":"x-table\/x-table",
 *                     "rules":[],
 *                     "length":421,
 *                     "keys":{
 *                   	 "temp1":421,
 *                   	 "temp2":421
 *                     },
 *                     "loc":null
 *               	}
 *               }
 *            }
 *         }
 *      }
 *   }
 */
$app->post('/table',
    function () use ($app,$auth,$ething) {
		$r = $ething->create($auth->user(),'Table',(array)Utils\getJSON($app),$auth->device());
		if(!$r) throw new \Utils\Exception('Unable to create the table');
		$app->response()->setStatus(201);
		$app->contentType('application/json');
		echo Utils\jsonEncodeFilterByFields($r,Utils\getParameter('fields',Utils\CHK_STRING_ARRAY, true, null));
    }
);

/**
 * @swagger-path
 * "/table/{id}":{  
 *      "get":{
 *         "tags": ["table"],
 *         "security":[{"access_token":[]}],
 *         "description":"
Retrieves the content of a table.

#### cURL examples

```bash
# get all the data of a table :
curl -H 'X-API-KEY: <YOUR_API_KEY>' http://localhost/ething/api/table/<TABLE_ID>

# only the first 20 rows :
curl -H 'X-API-KEY: <YOUR_API_KEY>' http://localhost/ething/api/table/<TABLE_ID>?start=0&length=20

# only the last 20 rows :
curl -H 'X-API-KEY: <YOUR_API_KEY>' http://localhost/ething/api/table/<TABLE_ID>?start=-20

# only the last 10 rows sorted by the field \"temperature\" in ascending order
# (put a minus before the name of the field if you want to sort in descending order)
curl -H 'X-API-KEY: <YOUR_API_KEY>' http://localhost/ething/api/table/<TABLE_ID>?start=-10&sort=temperature
```

",
 *         "produces": ["application/json","text/plain"],
 *         "parameters":[  
 *            {  
 *               "name":"id",
 *               "in":"path",
 *               "description":"id of the resource",
 *               "required":true,
 *               "type":"string"
 *            },
 *            {  
 *               "name":"start",
 *               "in":"query",
 *               "description":"Position of the first rows to return. If start is negative, the position will start from the end. (default to 0)",
 *               "required":false,
 *               "default":0,
 *               "type":"integer"
 *            },
 *            {  
 *               "name":"length",
 *               "in":"query",
 *               "description":"Maximum number of rows to return. If not set, returns until the end.",
 *               "required":false,
 *               "minimum":0,
 *               "type":"integer"
 *            },
 *            {  
 *               "name":"sort",
 *               "in":"query",
 *               "description":"the key on which to do the sorting, by default the sort is made by date ascending. To make the sort descending, prepend the field name by minus '-'. For instance, '-date' will sort by date descending ",
 *               "required":false,
 *               "default":"+date",
 *               "type":"string"
 *            },
 *            {  
 *               "name":"q",
 *               "in":"query",
 *               "description":"Query string for filtering results",
 *               "required":false,
 *               "type":"string"
 *            },
 *            {  
 *               "name":"fmt",
 *               "in":"query",
 *               "description":"the output format (default to JSON)",
 *               "required":false,
 *               "default":"JSON",
 *               "type":"string",
 *               "enum":["JSON","JSON_PRETTY","CSV","CSV_NO_HEADER"]
 *            },
 *            {  
 *               "name":"datefmt",
 *               "in":"query",
 *               "description":"the format of the date field (default to RFC3339)",
 *               "required":false,
 *               "default":"RFC3339",
 *               "type":"string",
 *               "enum":["RFC3339","TIMESTAMP"]
 *            }
 *         ],
 *         "responses":{
 *            "200":{
 *               "description":"The records of this table",
 *               "schema":{
 *                  "type":"array",
 *               	"items":{
 *               	   "type":"object",
 *               	   "description":"record's object. Every record has at least the 'id' and 'date' keys.",
 * 	             	   "properties":{  
 * 	             	   	"id":{  
 * 	             	   	   "type":"string",
 * 	             	   	   "description":"an unique id to identify a record"
 * 	             	   	},
 * 	             	   	"date":{  
 * 	             	   	   "type":"string",
 * 	             	   	   "format":"date-time",
 * 	             	   	   "description":"the create date of this record"
 * 	             	   	}
 *               	   }
 *               	}
 *               },
 *               "examples":{
 *               	"application/json": {
 *                     "id":"56c2-H3",
 *                     "date":"2016-02-15T22:47:20+00:00",
 *                     "pressure":100719,
 *                     "temperature":21.563,
 *                     "humidity":35
 *               	}
 *               }
 *            }
 *         }
 *      }
 *   }
 */
$app->get('/table/:id',
    function ($id) use ($app,$auth,$ething) {
		$r = Utils\getResource($auth, $id, 'Table');
		$app->lastModified($r->modifiedDate());
			
		$start = Utils\getParameter('START',Utils\CHK_INT,true,0);
		$length = Utils\getParameter('LENGTH',Utils\CHK_UNSIGNED_INT,true,null);
		$fields = Utils\getParameter('FIELDS',Utils\CHK_STRING_ARRAY,true,null);
		$format = Utils\getParameter('FMT',Utils\CHK_FORMAT,true,Utils\FMT_JSON);
		$sort = Utils\getParameter('SORT',Utils\CHK_STRING,true,null);
		$query = Utils\getParameter('Q',Utils\CHK_STRING,true,null);
		\Ething\Table::$dateFormat = Utils\getParameter('DATEFMT',Utils\CHK_DATEFORMAT,true,\DateTime::RFC3339);
		
		$selection = $r->select($start,$length,$fields,$sort,$query);
		
		if($format==Utils\FMT_JSON || $format==Utils\FMT_JSON_PRETTY){
			$app->contentType('application/json');
			echo json_encode($selection, ($format==Utils\FMT_JSON_PRETTY ? JSON_PRETTY_PRINT : 0)|JSON_UNESCAPED_SLASHES);
		}
		else if($format==Utils\FMT_CSV || $format==Utils\FMT_CSV_NOHEADER){
			if(is_null($fields))
				$fields = array_merge(array('id','date'),array_keys($r->keys()));
			$app->contentType('text/plain');
			Utils\csv_encode($selection, $fields, $format!=Utils\FMT_CSV_NOHEADER);
		}
    }
);

/**
 * @swagger-path
 * "/table/{id}":{  
 *      "put":{
 *         "tags": ["table"],
 *         "security":[{"access_token":[]}],
 *         "description":"Set the content of a table. The new data will erase the previous one.",
 *         "parameters":[  
 *            {  
 *               "name":"id",
 *               "in":"path",
 *               "description":"id of the resource",
 *               "required":true,
 *               "type":"string"
 *            },
 *            {  
 *               "name":"invalid_field",
 *               "in":"query",
 *               "description":"The behaviour to adopt when an invalid field name appears.",
 *               "required":false,
 *               "default":"rename",
 *               "type":"string",
 *               "enum":["rename","stop","skip","none"]
 *            },
 *            {  
 *               "name":"skip_error",
 *               "in":"query",
 *               "description":"Whether to skip data on error or not.",
 *               "required":false,
 *               "default":true,
 *               "type":"boolean"
 *            },
 *            {
 *               "name":"content",
 *               "in":"body",
 *               "description":"The content to be inserted as an array of object.
 
The data must be sent in a JSON formatted object :

```json
[{
	\"<KEY>\":<VALUE>
}]
```

example:

```json
[
	{
	  \"date\": \"2016-02-06T15:03:07+01:00\",
	  \"temperature\": 12.5,
	  \"pressure\": 101325
	},
	{
	  \"date\": \"2016-02-06T16:03:07+01:00\",
	  \"temperature\": 13.5,
	  \"pressure\": 101212
	}
]
```

If the 'date' field is not present, the current date will be set automatically.
If an 'id' field is present, it will be automatically be resetted to a new value.
 
 ",
 *               "required":true,
 *               "schema":{
 *                 "type": "array",
 *                 "items": {
 *               	  "type": "object"
 *                 }
 *               }
 *            }
 *         ],
 *         "responses":{
 *            "200":{
 *               "description":"The content was successfully set. The table metadata is returned.",
 *               "schema":{
 *               	"$ref":"#/definitions/Table"
 *               }
 *            }
 *         }
 *      }
 *   }
 */
$app->put('/table/:id',
    function ($id) use ($app,$auth,$ething) {
		$r = Utils\getResource($auth, $id, 'Table');
		
		$data = Utils\getJSON($app,true);
		
		$invalidFieldMode = Utils\getParameter('INVALID_FIELD',Utils\CHK_INVALIDFIELDMODE,true,\Ething\Table::INVALID_FIELD_RENAME);
		$skipError = Utils\getParameter('SKIP_ERROR',Utils\CHK_LOGIC,true,true);
		
		if(!empty($data)){
		
			Utils\spaceControl($auth,mb_strlen($app->request->getBody(), '8bit'));
			
			$r->import($data,$invalidFieldMode,$skipError);
			
			$app->contentType('application/json');
			echo Utils\jsonEncodeFilterByFields($r,Utils\getParameter('fields',Utils\CHK_STRING_ARRAY, true, null));
		}
		else {
			throw new \Utils\Exception('No POST data.');
		}
		
    }
);


/**
 * @swagger-path
 * "/table/{id}":{  
 *      "post":{
 *         "tags": ["table"],
 *         "security":[{"access_token":[]}],
 *         "description":"Insert a new record in a table",
 *         "parameters":[  
 *            {  
 *               "name":"id",
 *               "in":"path",
 *               "description":"id of the resource",
 *               "required":true,
 *               "type":"string"
 *            },
 *            {  
 *               "name":"invalid_field",
 *               "in":"query",
 *               "description":"The behaviour to adopt when an invalid field name appears.",
 *               "required":false,
 *               "default":"rename",
 *               "type":"string",
 *               "enum":["rename","stop","skip","none"]
 *            },
 *            {
 *               "name":"record",
 *               "in":"body",
 *               "description":"The record to be inserted.
 
The data must be sent in a JSON formatted object :

```json
{
	\"<KEY>\":<VALUE>
}
```

cURL example :

```bash
curl
	-H 'X-API-KEY: <YOUR_API_KEY>'
	-H \"Content-Type: application/json\"
	-X POST
	-d '{\"temperature\":15.2, \"comment\":\"outdoor\"}'
	http://localhost/ething/api/table/<TABLE_ID>
```

 
 ",
 *               "required":true,
 *               "schema":{
 *               	"type":"object"
 *               }
 *            }
 *         ],
 *         "responses":{
 *            "200":{
 *               "description":"The record was successfully inserted. The table metadata is returned.",
 *               "schema":{
 *               	"$ref":"#/definitions/Table"
 *               }
 *            }
 *         }
 *      }
 *   }
 */
$app->post('/table/:id',
    function ($id) use ($app,$auth,$ething) {
		$r = Utils\getResource($auth, $id, 'Table');
		
		$data = ($app->request->getMediaType() === 'application/json') ? Utils\getJSON($app,true) : $app->request->post();
		
		$invalidFieldMode = Utils\getParameter('INVALID_FIELD',Utils\CHK_INVALIDFIELDMODE,true,\Ething\Table::INVALID_FIELD_RENAME);
		
		if(!empty($data)){
		
			Utils\spaceControl($auth,mb_strlen($app->request->getBody(), '8bit'));
			
			$r->insert($data, $invalidFieldMode);
			$app->contentType('application/json');
			echo Utils\jsonEncodeFilterByFields($r,Utils\getParameter('fields',Utils\CHK_STRING_ARRAY, true, null));
		}
		else {
			throw new \Utils\Exception('No POST data.');
		}
		
    }
);

/**
 * @swagger-path
 * "/table/{id}/remove":{  
 *      "post":{
 *         "tags": ["table"],
 *         "security":[{"access_token":[]}],
 *         "description":"Remove one or more records in a table",
 *         "parameters":[  
 *            {  
 *               "name":"id",
 *               "in":"path",
 *               "description":"id of the resource",
 *               "required":true,
 *               "type":"string"
 *            },
 *            {
 *               "name":"recordIds",
 *               "in":"body",
 *               "description":"The records to be removed.",
 *               "required":true,
 *               "schema":{
 *               	"type":"array",
 *               	"items":{
 *               		"type":"string"
 *               	}
 *               }
 *            }
 *         ],
 *         "responses":{
 *            "200":{
 *               "description":"The records was successfully deleted",
 *               "schema":{
 *               	"$ref":"#/definitions/Table"
 *               }
 *            }
 *         }
 *      }
 *   }
 */
// delete multiple rows
$app->post('/table/:id/remove',
    function ($id) use ($app,$auth,$ething) {
		$r = Utils\getResource($auth, $id, 'Table');
		
		$data = ($app->request->getMediaType() === 'application/json') ? Utils\getJSON($app) : $app->request->post('id');
		
		if(!(is_array($data) && count($data) && array_reduce($data,function($carry,$item){return $carry && Utils\validId($item);},true))){
			throw new \Utils\Exception('Must be an array of record ids.');
		}
		
		$nb = $r->remove_rows($data);
		
		if($nb == count($data)){
			// all the specified documents/rows were removed
			$app->contentType('application/json');
			echo Utils\jsonEncodeFilterByFields($r,Utils\getParameter('fields',Utils\CHK_STRING_ARRAY, true, null));
		}
		else {
			// all or only certain documents/rows could not have been removed
			throw new \Utils\Exception('Some or all documents could not have been removed.');
		}
    }
);



// returns a single document in a table

// by id

$app->get('/table/:id/id/:docId',
    function ($id,$docId) use ($app,$auth,$ething) {
		$r = Utils\getResource($auth, $id, 'Table');
		$app->lastModified($r->modifiedDate());
		
		Utils\check(Utils\CHK_ID,$docId);
		
		if($doc = $r->get($docIdentifier)){
			$app->contentType('application/json');
			echo Utils\jsonEncodeFilterByFields($doc,Utils\getParameter('fields',Utils\CHK_STRING_ARRAY, true, null));
		}
		else
			throw new \Utils\Exception('The document does not exist.');
    }
);

$app->delete('/table/:id/id/:docId',
    function ($id,$docId) use ($app,$auth,$ething) {
		$r = Utils\getResource($auth, $id, 'Table');
		$app->lastModified($r->modifiedDate());
		
		Utils\check(Utils\CHK_ID,$docId);
		
		if($doc = $r->get($docIdentifier)){
			$r->remove_rows($doc->id);
			$app->contentType('application/json');
			echo Utils\jsonEncodeFilterByFields($doc,Utils\getParameter('fields',Utils\CHK_STRING_ARRAY, true, null));
		}
		else
			throw new \Utils\Exception('The document does not exist.');
    }
);

$app->get('/table/:id/id/:docId/:field',
    function ($id,$docId,$field) use ($app,$auth,$ething) {
		$r = Utils\getResource($auth, $id, 'Table');
		$app->lastModified($r->modifiedDate());
		
		Utils\check(Utils\CHK_ID,$docId);
		
		if($doc = $r->get($docIdentifier)){
			if(array_key_exists($field,$doc)){
				$content = $doc->$field;
				$finfo = new finfo(FILEINFO_MIME);
				$app->contentType($finfo->buffer($content));
				echo $content;
			}
			else
				throw new \Utils\Exception('The field "'.$field.'" does not exist.');
		}
		else
			throw new \Utils\Exception('The document does not exist.');
    }
);

// by index

$app->get('/table/:id/index/:index',
    function ($id,$index) use ($app,$auth,$ething) {
		$r = Utils\getResource($auth, $id, 'Table');
		$app->lastModified($r->modifiedDate());
		
		Utils\check(Utils\CHK_INT,$index);
		
		$doc = $r->select($index,1);
		if(count($doc)){
			$doc = $doc[0];
			$app->contentType('application/json');
			echo Utils\jsonEncodeFilterByFields($doc,Utils\getParameter('fields',Utils\CHK_STRING_ARRAY, true, null));
		}
		else
			throw new \Utils\Exception('Index out of bound.');
    }
);

$app->delete('/table/:id/index/:index',
    function ($id,$index) use ($app,$auth,$ething) {
		$r = Utils\getResource($auth, $id, 'Table');
		$app->lastModified($r->modifiedDate());
		
		Utils\check(Utils\CHK_INT,$index);
		
		$doc = $r->select($index,1);
		if(count($doc)){
			$doc = $doc[0];
			$r->remove_rows($doc->id);
			$app->contentType('application/json');
			echo Utils\jsonEncodeFilterByFields($doc,Utils\getParameter('fields',Utils\CHK_STRING_ARRAY, true, null));
		}
		else
			throw new \Utils\Exception('Index out of bound.');
		
    }
);

$app->get('/table/:id/index/:index/:field',
    function ($id,$index,$field) use ($app,$auth,$ething) {
		$r = Utils\getResource($auth, $id, 'Table');
		$app->lastModified($r->modifiedDate());
		
		Utils\check(Utils\CHK_INT,$index);
		
		$doc = $r->select($index,1);
		if(count($doc)){
			$doc = $doc[0];
			if(array_key_exists($field,$doc)){
				$content = $doc->$field;
				$finfo = new finfo(FILEINFO_MIME);
				$app->contentType($finfo->buffer($content));
				echo $content;
			}
			else
				throw new \Utils\Exception('The field "'.$field.'" does not exist.');
		}
		else
			throw new \Utils\Exception('Index out of bound.');
		
    }
);



/**
 * @swagger-path
 * "/app":{  
 *      "get":{
 *         "tags": ["app"],
 *         "security":[{"access_token":[]}],
 *         "description":"Lists the user's applications",
 *         "parameters":[ 
 *            {  
 *               "name":"limit",
 *               "in":"query",
 *               "description":"Limits the number of applications returned",
 *               "required":false,
 *               "type":"integer"
 *            },
 *            {  
 *               "name":"skip",
 *               "in":"query",
 *               "description":"Skips a number of applications",
 *               "required":false,
 *               "type":"integer"
 *            }
 *         ],
 *         "responses":{
 *            "200":{
 *               "description":"A list of applications",
 *               "schema":{
 *                  "type":"array",
 *                  "items":{  
 *                     "$ref":"#/definitions/App"
 *                  }
 *               }
 *            }
 *         }
 *      }
 *   }
 */
$app->get('/app',
    function () use ($app,$auth,$ething) {
		$app->contentType('application/json');
		echo Utils\jsonEncodeFilterByFields($auth->fs()->all(
			'type == "App"',
			Utils\getParameter('limit',Utils\CHK_UNSIGNED_INT, true, null),
			Utils\getParameter('skip',Utils\CHK_UNSIGNED_INT, true, null)
		),Utils\getParameter('fields',Utils\CHK_STRING_ARRAY, true, null));
    }
);

/**
 * @swagger-path
 * "/app":{  
 *      "post":{
 *         "tags": ["app"],
 *         "security":[{"access_token":[]}],
 *         "description":"
Creates a new application.

There are 2 ways to pass directly the code and the icon data of the application on the same request :

 - pass the code or/and the icon data as a base-64 encoded ASCII string through the key 'content' and 'icon' respectively of the metadata object.
 
 example:

```json
{
   \"name\": \"myapp\",
   \"content\": \"SGVsb...GQgIQ==\", // your code in base-64
   \"icon\": \"bXkga...biBkYXRh\" // your icon data in base-64
}
```

 - multipart/related request: transfers the code and/or the icon binary data along with metadata. The order of the different part does not matter. The code part must have the Content-Type header set to 'text/html' or 'text/plain'.
   The icon part must have the Content-Type header set to a compatible image MIME type.
 
 example:
 
```
POST /ething/api/app HTTP/1.1
Host: <YOUR_HOST>
Content-Type: multipart/related; boundary=foo_bar_baz

--foo_bar_baz
Content-Type: application/json; charset=UTF-8

{
  \"name\": \"myapp\"
}

--foo_bar_baz
Content-Type: image/jpeg

<JPEG DATA>

--foo_bar_baz
Content-Type: text/html

<!doctype html>
<html lang=\"en\">
<head>
  <meta charset=\"utf-8\">
  <title>myapp</title>
</head>
<body>
  Hello World !
</body>
</html>
--foo_bar_baz--
```

",
 *         "parameters":[  
 *            {  
 *               "name":"metadata",
 *               "in":"body",
 *               "description":"The metadata of the application to be created.",
 *               "required":true,
 *               "schema":{
 *               	"$ref":"#/definitions/App"
 *               }
 *            }
 *         ],
 *         "responses":{
 *            "200":{
 *               "description":"The application was successfully created",
 *               "schema":{
 *               	"$ref":"#/definitions/App"
 *               }
 *            }
 *         }
 *      }
 *   }
 */
$app->post('/app',
    function () use ($app,$auth,$ething) {
		
		$multipart = Utils\readMultipartRelated();
		if($multipart){
			
			function check($multipart){
				
				$d = array(
					'attr' => null,
					'script' => null,
					'icon' => null
				);
				
				foreach($multipart as $i => $part){
					
					$contentType = isset($part['headers']['Content-Type']) ? Utils\getMediaType($part['headers']['Content-Type']) : 'text/plain';
					
					if(!$d['attr'] && $contentType==='application/json'){
						$d['attr'] = json_decode($part['body'], true);
						if(json_last_error() !== JSON_ERROR_NONE)
							throw new \Utils\Exception('Invalid JSON: '.json_last_error_msg());
					}
					else if(!$d['script'] && ($contentType==='text/html' || $contentType==='text/plain')){
						$d['script'] = $part['body'];
					}
					else if(!$d['icon'] && preg_match('/^image\/[-\w]+$/', $contentType)){
						$d['icon'] = $part['body'];
					}
					else
						return null;
				}
				
				return $d['attr'] ? $d : null;
			}
			
			if(!($d = check($multipart)))
				throw new \Utils\Exception('invalid multipart/related content');
			
			$attr = $d['attr'];
			
			if(isset($d['script']) && !isset($attr['script']))
				$attr['script'] = $d['script'];
			
			if(isset($d['icon']) && !isset($attr['icon']))
				$attr['icon'] = $d['icon'];
		}
		else
			$attr = (array)Utils\getJSON($app);
		
		
		$r = $ething->create($auth->user(),'App',$attr,$auth->device());
		if(!$r) throw new \Utils\Exception('Unable to create the app');
		$app->response()->setStatus(201);
		$app->contentType('application/json');
		echo Utils\jsonEncodeFilterByFields($r,Utils\getParameter('fields',Utils\CHK_STRING_ARRAY, true, null));
    }
);

/**
 * @swagger-path
 * "/app/{id}":{  
 *      "get":{
 *         "tags": ["app"],
 *         "security":[{"access_token":[]}],
 *         "description":"Retrieves the script of an application",
 *         "parameters":[  
 *            {  
 *               "name":"id",
 *               "in":"path",
 *               "description":"id of the resource",
 *               "required":true,
 *               "type":"string"
 *            }
 *         ],
 *         "produces":["text/html"],
 *         "responses":{
 *            "200":{
 *               "description":"The source code",
 *               "schema": {
 *               	"type": "file"
 *               }
 *            }
 *         }
 *      },
 *      "put":{
 *         "tags": ["app"],
 *         "security":[{"access_token":[]}],
 *         "description":"Set the script for this application. The script must be a single HTML page.",
 *         "parameters":[  
 *            {  
 *               "name":"id",
 *               "in":"path",
 *               "description":"id of the resource",
 *               "required":true,
 *               "type":"string"
 *            },
 *            {  
 *               "name":"script",
 *               "in":"body",
 *               "description":"The script as a HTML page.",
 *               "required":true,
 *               "schema": {
 *               	"type": "string",
 *               	"format": "binary"
 *               }
 *            }
 *         ],
 *         "consumes":["text/plain","text/html"],
 *         "responses":{
 *            "200":{
 *               "description":"The script was set successfully. It returns back the meta data of this application.",
 *               "schema": {
 *               	"$ref":"#/definitions/App"
 *               }
 *            }
 *         }
 *      }
 *   }
 */
$app->get('/app/:id',
    function ($id) use ($app,$auth,$ething) {
		$r = Utils\getResource($auth, $id, 'App');
		$app->lastModified($r->modifiedDate());
		$app->contentType('text/html');
		echo $r->readScript();
    }
);

$app->put('/app/:id',
    function ($id) use ($app,$auth,$ething) {
		$r = Utils\getResource($auth, $id, 'App');
		$acceptedMime = array("text/plain","text/html");
		if(!in_array($app->request->getMediaType(),$acceptedMime))
			throw new \Utils\Exception('The script must be one of the following format : '.implode(', ',$acceptedMime));
		$bytes = $app->request->getBody();
		Utils\spaceControl($auth,mb_strlen($bytes, '8bit'));
		$r->setScript($bytes);
		$app->contentType('application/json');
		echo Utils\jsonEncodeFilterByFields($r,Utils\getParameter('fields',Utils\CHK_STRING_ARRAY, true, null));
    }
);

/**
 * @swagger-path
 * "/app/{id}/icon":{  
 *      "get":{
 *         "tags": ["app"],
 *         "security":[{"access_token":[]}],
 *         "description":"Retrieves the icon of an application if there is one defined.",
 *         "parameters":[  
 *            {  
 *               "name":"id",
 *               "in":"path",
 *               "description":"id of the resource",
 *               "required":true,
 *               "type":"string"
 *            }
 *         ],
 *         "produces":["image/jpeg","image/png"],
 *         "responses":{
 *            "200":{
 *               "description":"The icon of this application.",
 *               "schema": {
 *               	"type":"file"
 *               }
 *            }
 *         }
 *      }
 *   }
 */
$app->get('/app/:id/icon',
    function ($id) use ($app,$auth,$ething) {
		$r = Utils\getResource($auth, $id, 'App');
		$app->lastModified($r->modifiedDate());
		$content = $r->readIcon();
		if(is_null($content))
			throw new \Utils\Exception('No icon available',404);
		$finfo = new finfo(FILEINFO_MIME);
		$app->contentType($finfo->buffer($content));
		echo $content;
    }
);





/**
 * @swagger-path
 * "/device":{  
 *      "get":{
 *         "tags": ["device"],
 *         "security":[{"access_token":[]}],
 *         "description":"Lists the user's devices",
 *         "parameters":[ 
 *            {  
 *               "name":"limit",
 *               "in":"query",
 *               "description":"Limits the number of devices returned",
 *               "required":false,
 *               "type":"integer"
 *            },
 *            {  
 *               "name":"skip",
 *               "in":"query",
 *               "description":"Skips a number of devices",
 *               "required":false,
 *               "type":"integer"
 *            }
 *         ],
 *         "responses":{
 *            "200":{
 *               "description":"A list of devices",
 *               "schema":{
 *                  "type":"array",
 *                  "items":{  
 *                     "$ref":"#/definitions/Device"
 *                  }
 *               }
 *            }
 *         }
 *      }
 *   }
 */
$app->get('/device',
    function () use ($app,$auth,$ething) {
		$app->contentType('application/json');
		echo Utils\jsonEncodeFilterByFields($auth->fs()->all(
			'type == "Device"',
			Utils\getParameter('limit',Utils\CHK_UNSIGNED_INT, true, null),
			Utils\getParameter('skip',Utils\CHK_UNSIGNED_INT, true, null)
		),Utils\getParameter('fields',Utils\CHK_STRING_ARRAY, true, null));
    }
);

/**
 * @swagger-path
 * "/device":{  
 *      "post":{
 *         "tags": ["device"],
 *         "security":[{"access_token":[]}],
 *         "description":"Creates a new device",
 *         "parameters":[  
 *            {  
 *               "name":"metadata",
 *               "in":"body",
 *               "description":"
The metadata of the device to be created.

example:

```json
{
   \"name\": \"mydevice.txt\",
   \"loc\": \"Toulouse, France\"
}
```
",
 *               "required":true,
 *               "schema":{
 *               	"$ref":"#/definitions/Device"
 *               }
 *            }
 *         ],
 *         "responses":{
 *            "200":{
 *               "description":"The device was successfully created",
 *               "schema":{
 *               	"$ref":"#/definitions/Device"
 *               }
 *            }
 *         }
 *      }
 *   }
 */
$app->post('/device',
    function () use ($app,$auth,$ething) {
		$r = $ething->create($auth->user(),'Device',(array)Utils\getJSON($app),$auth->device());
		if(!$r) throw new \Utils\Exception('Unable to create the device');
		$app->response()->setStatus(201);
		$app->contentType('application/json');
		echo Utils\jsonEncodeFilterByFields($r,Utils\getParameter('fields',Utils\CHK_STRING_ARRAY, true, null));
    }
);


/**
 * @swagger-path
 * "/device/{id}/apikey":{  
 *      "get":{
 *         "tags": ["device"],
 *         "security":[{"access_token":[]}],
 *         "description":"Gets the API key of a device",
 *         "parameters":[  
 *            {  
 *               "name":"id",
 *               "in":"path",
 *               "description":"id of the resource",
 *               "required":true,
 *               "type":"string"
 *            }
 *         ],
 *         "responses":{
 *            "200":{
 *               "description":"The API key of the current device",
 *               "schema":{
 *               	"type":"object",
 * 	                "properties":{  
 * 	                	"key":{
 * 	                	   "type":"string",
 * 	                	   "description":"key"
 * 	                	}
 *                  }
 *               }
 *            }
 *         }
 *      }
 *   }
 */
$app->get('/device/:id/apikey',
    function ($id) use ($app,$auth,$ething) {
		$r = Utils\getResource($auth, $id, 'Device');
		$app->contentType('application/json');
		echo json_encode($r->apiKey(),JSON_PRETTY_PRINT|JSON_UNESCAPED_SLASHES);
    }
);

/**
 * @swagger-path
 * "/device/{id}/request/{path}":{  
 *      "get":{
 *         "tags": ["device"],
 *         "security":[{"access_token":[]}],
 *         "summary":"send a GET request to a device.",
 *         "description":"Forward this HTTP request to a device with the specified path.",
 *         "responses":{
 *           "default":{
 *              "description":"The answer from the device"
 *           }
 *         }
 *      },
 *      "post":{
 *         "tags": ["device"],
 *         "security":[{"access_token":[]}],
 *         "summary":"send a POST request to a device.",
 *         "description":"Forward this HTTP request to a device with the specified path.",
 *         "responses":{
 *           "default":{
 *              "description":"The answer from the device"
 *           }
 *         }
 *      },
 *      "put":{
 *         "tags": ["device"],
 *         "security":[{"access_token":[]}],
 *         "summary":"send a PUT request to a device.",
 *         "description":"Forward this HTTP request to a device with the specified path.",
 *         "responses":{
 *           "default":{
 *              "description":"The answer from the device"
 *           }
 *         }
 *      },
 *      "delete":{
 *         "tags": ["device"],
 *         "security":[{"access_token":[]}],
 *         "summary":"send a DELETE request to a device.",
 *         "description":"Forward this HTTP request to a device with the specified path.",
 *         "responses":{
 *           "default":{
 *              "description":"The answer from the device"
 *           }
 *         }
 *      },
 *      "patch":{
 *         "tags": ["device"],
 *         "security":[{"access_token":[]}],
 *         "summary":"send a PATCH request to a device.",
 *         "description":"Forward this HTTP request to a device with the specified path.",
 *         "responses":{
 *           "default":{
 *              "description":"The answer from the device"
 *           }
 *         }
 *      },
 *      "parameters":[  
 *         {  
 *            "name":"id",
 *            "in":"path",
 *            "description":"id of the resource",
 *            "required":true,
 *            "type":"string"
 *         },
 *         {  
 *            "name":"path",
 *            "in":"path",
 *            "description":"the path of the HTTP request including an optional query string",
 *            "required":true,
 *            "type":"string"
 *         }
 *      ]
 *   }
 */
$app->any('/device/:id/request(/(:path+))',
    function ($id) use ($app,$auth,$ething) {
		
		$args = func_get_args();
		$path = (count($args)>1) ? $args[1] : array();
		
		$r = Utils\getResource($auth, $id, 'Device');
		$path = implode('/',$path);
		// send the current request to the specified device
		$query = \Ething\Proxy::getQuery();
		if(!empty($query)) $path .= '?'.$query;
		
		$r->forward($path, function($path,$device) use ($app){
			$url = $app->request->getRootUri().'/device/'.$device->id().'/request'.$path;
			
			// append the black listed query parameters
			$query = array();
			foreach(\Ething\Proxy::$blackListQuery as $key){
				if(isset($_GET[$key]))
					$query[$key] = $_GET[$key];
			}
			if(!empty($query)){
				$url .= empty(parse_url($url,PHP_URL_QUERY)) ? '?' : '&';
				$url .= http_build_query($query);
			}
			
			return $url;
		});
		
    }
);


/**
 * @swagger-path
 * "/device/{id}/descriptor":{  
 *      "get":{
 *         "tags": ["device"],
 *         "security":[{"access_token":[]}],
 *         "description":"Retrieves the descriptor of a device. Only device with an URL set has a descriptor. The descriptor is an object based on the Swagger specification",
 *         "parameters":[  
 *            {  
 *               "name":"id",
 *               "in":"path",
 *               "description":"id of the resource",
 *               "required":true,
 *               "type":"string"
 *            }
 *         ],
 *         "produces":["application/json"],
 *         "responses":{
 *            "200":{
 *               "description":"The descriptor of this device.",
 *               "schema": {
 *               	"type":"file"
 *               }
 *            }
 *         }
 *      }
 *   }
 */
$app->get('/device/:id/descriptor',
    function ($id) use ($app,$auth,$ething) {
		$r = Utils\getResource($auth, $id, 'Device');
		$app->lastModified($r->modifiedDate());
		$descriptor = $r->getDescriptor();
		if(!$descriptor)
			throw new \Utils\Exception('No descriptor available',404);
		$app->contentType('application/json');
		echo json_encode($descriptor,JSON_PRETTY_PRINT|JSON_UNESCAPED_SLASHES);
    }
);



 
/**
 * @swagger-path
 * "/notification":{  
 *      "post":{
 *         "security":[{"access_token":[]}],
 *         "description":"Send a notification to the current user.",
 *         "parameters":[  
 *            {  
 *               "name":"notification data",
 *               "in":"body",
 *               "description":"the data of the notification to be sent",
 *               "required":true,
 *               "schema":{
 *               	"type":"object",
 * 	                "properties":{  
 * 	                	"subject":{
 * 	                	   "type":"string",
 * 	                	   "description":"the subject of the notification (default to 'notification')"
 * 	                	},
 * 	                	"body":{
 * 	                	   "type":"string",
 * 	                	   "description":"the content of the notification"
 * 	                	}
 *                  }
 *               }
 *            }
 *         ],
 *         "responses":{
 *            "200":{
 *               "description":"The notification was successfully sent"
 *            }
 *         }
 *      }
 *   }
 */
$app->post('/notification',
    function () use ($app,$auth,$ething) {
		$noti = array_merge(array(
			'subject' => null,
			'body' => null
		),Utils\getJSON($app,true));
		$auth->user()->sendMail($noti['subject'],$noti['body']);
    }
);
 



$app->any('/proxy',
    function () use ($app,$auth,$ething) {
		$url = Utils\getParameter('url',Utils\CHK_URL);
		
		$curl_options = array();

		// auth ?
		$auth = $app->request->headers->get('X-AUTH');
		if(!$auth)
			$auth = $app->request->get('auth');
		if($auth){
			$a = explode(';',$auth);
			if(is_array($a) && count($a)==3){
				$a = array_map('urldecode',$a);
				$mode = strtolower($a[0]);
				$user = $a[1];
				$password = $a[2];
				switch($mode){
					case 'basic':
						$curl_options[CURLOPT_HTTPAUTH] = CURLAUTH_BASIC; // The HTTP authentication method(s) to use.
						break;
					case 'digest':
						$curl_options[CURLOPT_HTTPAUTH] = CURLAUTH_DIGEST; // The HTTP authentication method(s) to use.
						break;
				}
				$curl_options[CURLOPT_USERPWD] = $user.':'.$password;
			}
		}
		
		\Ething\Proxy::$blackListHeaders[] = 'X-AUTH';
		
		$p = new \Ething\Proxy($ething);
		$p->setUrlProxify(function($url){
			return preg_replace('/(?<=(\?|&))url=[^&#]*/','url='.urlencode($url),$_SERVER['REQUEST_URI']);
		});
		$p->forward($url, $curl_options);
    }
);









/*
* error handler
*/

/**
 * @swagger-definition
 * "Error":{ 
 *   "type": "object",
 *   "description": "An object describing an error",
 * 	 "properties":{  
 * 		"message":{  
 * 		   "type":"string",
 * 		   "description":"A description of the error",
 *         "readOnly": true
 * 		},
 * 		"code":{  
 * 		   "type":"number",
 * 		   "description":"The HTTP response status code",
 *         "readOnly": true
 * 		}
 * 	 }
 * }
 */

$app->error(function (\Exception $e) use ($app,$auth,$ething,$debug) {
	
	$internalerr = $e->getCode() < 100 || $e->getCode() >= 600;
	
	// set the response code
	$responseCode = $internalerr ? 400 : $e->getCode();
	$app->response()->setStatus($responseCode);
	// send the error message as JSON
	$app->contentType('application/json');
	
	\Utils\log($e);
	
	if($debug){
		$error = array(
			'message' => $e->getMessage(),
			'trace' => $e->getTraceAsString(),
			'line' => $e->getLine(),
			'file' => $e->getFile(),
			'class' => get_class($e),
			'code' => $responseCode
		);
	}
	else {
		$error = array(
			'message' => (!$internalerr) ? $e->getMessage() : 'internal error',
			'code' => $responseCode
		);
	}
	echo json_encode($error,JSON_PRETTY_PRINT|JSON_UNESCAPED_SLASHES);
	
});

$app->notFound(function () use ($app,$auth,$ething) {
	
	// send the error message as JSON
	$app->contentType('application/json');
	echo json_encode(array(
		'message' => 'Not found',
		'code' => 404
	),JSON_PRETTY_PRINT|JSON_UNESCAPED_SLASHES);
	
});




/*
* Cache control
*/
require_once __DIR__.'/cache.php';
$app->add(new CacheMiddleware());



/*
* Authentification middleware
*/
$app->add($auth);


/*
* CORS middleware
*/
if(isset($config['cors']) && $config['cors']){
	require_once __DIR__.'/cors.php';
	$app->add(new CorsMiddleware());
}



$ething->setEventExceptionHandler(function($exception){
	\Utils\log($exception);
});
$ething->setDelayEvents(true);

$app->run();

if($ething->hasPendingEvents()){
	
	ignore_user_abort(true);
	set_time_limit(0);
	
	// send the response first
	ob_end_flush();
	flush();
	session_write_close();
	
	// dispatch the events
	$ething->dispatchPendingEvents();
	
}


