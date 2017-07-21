<?php

/**
 * @swagger
 * {  
 *      "swagger": "2.0",
 *      "info": {
 *         "title": "eThing HTTP api",
 *         "description": "
 
The eThing project is an 'Internet of Things' application. Store and retrieve data from your devices using simple HTTP requests.

This API describe how to access to your resources (file, table, device ...) through HTTP requests.

-------------


### Resource description

There are different types of resources. A resource can either be :

 - file : use this kind of objects to store text data or binary data (image, ...)
 - table : tables are used to store a collection of related data. Table consists of fields and rows.
 - device : this resource describes a device.
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

There are several options for authenticating with the API.

#### Basic authentication

HTTP Basic authentication is the simplest way of interacting with the API. 
Simply pass the username (always 'ething') and password with each request through the `Authorization` header.
This value should be encoded (using base64 encoding) as per the HTTP Basic specification.

```bash
curl -u username:password ...
```


#### API key

Every device or app has an API key. API keys are listed on developer page [http://<YOUR_SERVER_ADDRESS>/ething/client/#!developer](http://localhost/ething/client/#!developer).

API calls authenticated with API key are made on behalf of the Application or Device that own this it ! The permissions can be modified in the resource settings.

Send the following header below on every request :

```
GET /ething/api/resources HTTP/1.1
Host: localhost
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


The available fields for resource filtering :

 - 'type'
 - 'name'
 - 'mime'
 - 'id'
 - 'location.latitude'
 - 'location.longitude'
 - 'location.altitude'
 - 'createdDate'
 - 'modifiedDate'
 - 'createdBy'
 - 'createdBy.type'
 - 'createdBy.id'
 - 'description'
 - 'data.*'
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
 - Date : *RFC 3339* format,  e.g., *2015-03-24T12:00:00+02:00*. (All formats described here http://php.net/manual/en/datetime.formats.php are also available)

Constants :

 - 'me' : available only when using API key authentication method. It corresponds to the current Device or App.

 
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

Search for resources created by the current authenticated Device or App

`createdBy == me`

Search for resources with internal data \"temperature\" greater than 32

`data.temperature > 32`




### Scopes


Scopes let you specify exactly what type of data access your application or device needs.

| Scope          | Description                                                          |
|----------------|----------------------------------------------------------------------|
| resource:read  | read the content of any resource                                     |
| resource:write | create resources of any kind and modify the content of any resource  |
| resource:admin | modify resource properties, delete resource and access to apikeys    |
| file:read      | read the content of any file                                         |
| file:write     | create files and modify the content of any file                      |
| table:read     | read the content of any table                                        |
| table:write    | create tables and modify the content of any table                    |
| table:append   | append data to any existing table                                    |
| app:read       | execute apps                                                         |
| app:write      | create and edit apps                                                 |
| app:execute    | execute apps                                                         |
| device:read    | send GET request to any device                                       |
| device:write   | send POST,PUT,PATCH,DELETE request to any device                     |
| notification   | send notification                                                    |
| settings:read  | read the settings                                                |
| settings:write | modify the settings                                              |
| proxy:read     | send GET request through your local network                          |
| proxy:write    | send POST,PUT,PATCH,DELETE through your local network                |
| rule:read      | read rules attributes                                                |
| rule:write     | create rules                                                         |
| rule:execute   | execute rules                                                        |
| rule:admin     | delete rules                                                         |




 ",
 *         "version": "0.1.0"
 *      },
 *      "host": "localhost",
 *      "basePath": "/ething/api",
 *      "schemes": ["http"],
 *      "consumes": ["application/json"],
 *      "produces": ["application/json"],
 *      "securityDefinitions":{
 *        "api_key": {
 *          "type": "apiKey",
 *          "description": "authentication through an API key, used only by devices or apps.",
 *          "name": "X-API-KEY",
 *          "in": "header"
 *        },
 *        "api_key_query": {
 *          "type": "apiKey",
 *          "description": "authentication through an API key, used only by devices or apps.",
 *          "name": "api_key",
 *          "in": "query"
 *        },
 *        "basic_auth": {
 *          "type": "basic",
 *          "description": "basic authentication."
 *        }
 *      },
 *      "security":[ {"api_key":[]}, {"api_key_query":[]}, {"basic_auth":[]} ],
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
 *      		"name": "settings",
 *      		"description": "Operations to manage settings"
 *      	}
 *      ],
 *      "paths": []
 *   }
 */

$rootDir = __DIR__.'/..';

require_once __DIR__.'/utils.php';

// composer
require_once $rootDir.'/vendor/autoload.php';

$app = new \Slim\Slim(array(
    'debug' => false
));

require_once $rootDir.'/src/Ething.php';
$ething = new \Ething\Ething();

$debug = $ething->config('debug');

error_reporting($debug ? E_ALL : 0);




/* auth */
require_once __DIR__.'/auth.php';
$auth = new \Auth\HttpAuth($ething);

# never transmit these parameters/headers to any device
\Ething\Proxy::$deny_request_headers[] = 'X-API-KEY';
\Ething\Proxy::$deny_request_headers[] = 'X-AUTH';
\Ething\Proxy::$deny_request_headers[] = 'Cookie';
\Ething\Proxy::$deny_request_headers[] = 'x-csrf-token';
\Ething\Proxy::$deny_request_headers[] = 'Authorization';
\Ething\Proxy::$deny_request_query[] = 'api_key';
\Ething\Proxy::$deny_request_query[] = 'auth';



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
 * "/auth":{  
 *      "get":{
 *         "description":"Returns information about the current authentication. The properties \"device\" and \"app\" are only available with API key authentication.",
 *         "responses":{
 *            "200":{
 *               "description":"authentication information",
 *               "schema":{
 *                  "type":"object",
 * 	                "properties":{  
 * 	                	"scope":{
 * 	                	   "type":"string",
 * 	                	   "description":"The space-delimited set of permissions. If the field is missing, it means \"full permissions\"."
 * 	                	},
 * 	                	"device":{  
 * 	                	   "$ref":"#/definitions/Device"
 * 	                	},
 * 	                	"app":{
 * 	                	   "$ref":"#/definitions/App"
 * 	                	}
 *                  }
 *               }
 *            }
 *         }
 *      }
 *   }
 */
$app->get('/auth',
    function () use ($app,$auth) {
		
		$data = array(
			'type' => $auth->mode()
		);
		
		$originator = $auth->originator();
		
		if($originator instanceof \Ething\Device)
			$data['device'] = $originator;
		else if($originator instanceof \Ething\App)
			$data['app'] = $originator;
		
		if(!is_null($auth->scope()))
			$data['scope'] = $auth->scope();
		
		
		$app->contentType('application/json');
		echo json_encode($data,JSON_PRETTY_PRINT|JSON_UNESCAPED_SLASHES);
		
    }
);



/**
 * @swagger-path
 * "/settings":{  
 *      "get":{
 *         "tags": ["settings"],
 *         "description":"Returns the settings",
 *         "responses":{
 *            "200":{
 *               "description":"The settings",
 *               "schema":{
 *               	"$ref":"#/definitions/Settings"
 *               }
 *            }
 *         }
 *      }
 *   }
 */
$app->get('/settings',
    function () use ($app,$ething) {
		$app->contentType('application/json');
		echo json_encode($ething->config,JSON_PRETTY_PRINT|JSON_UNESCAPED_SLASHES);
		
    }
);

/**
 * @swagger-path
 * "/settings":{  
 *      "patch":{
 *         "tags": ["settings"],
 *         "description":"update your settings.",
 *         "parameters":[  
 *            {  
 *               "name":"data",
 *               "in":"body",
 *               "description":"the attributes to modify",
 *               "required":true,
 *               "schema":{
 *                  "$ref":"#/definitions/Settings"
 *               }
 *            }
 *         ],
 *         "responses":{
 *            "200":{
 *               "description":"settings successfully updated",
 *               "schema":{
 *                  "$ref":"#/definitions/Settings"
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
$app->patch('/settings',
    function () use ($app,$ething) {
		$ething->config->attr(Utils\getJSON($app));
		$ething->config->save();
		$app->contentType('application/json');
		echo json_encode($ething->config,JSON_PRETTY_PRINT|JSON_UNESCAPED_SLASHES);
    }
);



/**
 * @swagger-path
 * "/usage":{  
 *      "get":{
 *         "tags": ["resource"],
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
$app->get('/usage', $auth->permissions('resource:read'), 
    function () use ($app,$ething) {
		$app->contentType('application/json');
		echo json_encode($ething->stats(),JSON_PRETTY_PRINT|JSON_UNESCAPED_SLASHES);
    }
);



/**
 * @swagger-path
 * "/resources":{  
 *      "get":{
 *         "tags": ["resource"],
 *         "description":"
Lists the resources.

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

$app->get('/resources', $auth->permissions('resource:read resource:write file:read file:write table:read table:write table:append device:read device:write app:read app:write'),
    function () use ($app,$auth,$ething) {
		
		$query = Utils\getParameter('q',Utils\CHK_STRING, true, null);
		
		$scopes = $auth->scope();
		if($scopes !== null){
			$scopes = explode(' ', $scopes);
			
			$filteredTypes = array_reduce($scopes, function($filteredTypes, $scope){
				$type = explode(':',$scope,2)[0];
				if(!in_array($type, $filteredTypes))
					$filteredTypes[] = $type;
				return $filteredTypes;
			}, array());
			
			if(!in_array('resource', $filteredTypes)){
				
				$typeQuery = array(
					'type' => array( '$in' => array_map(function($type){
						return new \MongoDB\BSON\Regex("^$type");
					}, $filteredTypes) )
				);
				
				if(empty($query)){
					$query = $typeQuery;
				} else {
					// merge the query
					$query = array(
						'$and' => array( $ething->resourceQueryParser()->parse($query), $typeQuery )
					);
				}
			}
			
		}
		
		$app->contentType('application/json');
		echo Utils\jsonEncodeFilterByFields($ething->find(
			$query,
			Utils\getParameter('limit',Utils\CHK_UNSIGNED_INT, true, null),
			Utils\getParameter('skip',Utils\CHK_UNSIGNED_INT, true, null),
			Utils\getParameter('sort',Utils\CHK_STRING,true,null)
		),Utils\getParameter('fields',Utils\CHK_STRING_ARRAY, true, null));
    }
);



/**
 * @swagger-path
 * "/resources/{id}":{  
 *      "get":{
 *         "tags": ["resource"],
 *         "summary":"Gets the meta-data of a resource.",
 *         "description":"
 Returns the meta-data of a resource in JSON.
 ",
 *         "parameters":[  
 *            {  
 *               "name":"id",
 *               "in":"path",
 *               "description":"id of the resource. Devices or Apps using the api key authentication may use the word 'me' to replace their id.",
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
$app->get('/resources/:id', $auth->permissions('resource:read resource:write file:read file:write table:read table:write table:append device:read device:write app:read app:write'),
    function ($id) use ($app,$auth) {
		$r = Utils\getResource($auth, $id);
		
		$scopes = $auth->scope();
		if($scopes !== null){
			$scopes = explode(' ', $scopes);
			
			$filteredTypes = array_reduce($scopes, function($filteredTypes, $scope){
				$type = explode(':',$scope,2)[0];
				if(!in_array($type, $filteredTypes))
					$filteredTypes[] = $type;
				return $filteredTypes;
			}, array());
			
			if(!in_array('resource', $filteredTypes)){
				
				if(!in_array(strtolower($r->baseType()), $filteredTypes))
					throw new Exception('Unknown resource',404);
			}
			
		}
		
		$app->contentType('application/json');
		echo Utils\jsonEncodeFilterByFields($r,Utils\getParameter('fields',Utils\CHK_STRING_ARRAY, true, null));
    }
);

/**
 * @swagger-path
 * "/resources/{id}":{  
 *      "delete":{
 *         "tags": ["resource"],
 *         "description":"deletes a resource",
 *         "parameters":[  
 *            {  
 *               "name":"id",
 *               "in":"path",
 *               "description":"id of the resource. Devices or Apps using the api key authentication may use the word 'me' to replace their id.",
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
$app->delete('/resources/:id', $auth->permissions('resource:admin'),
    function ($id) use ($app,$auth) {
		$r = Utils\getResource($auth, $id);
		$r->remove();
    }
);

/**
 * @swagger-path
 * "/resources/{id}":{  
 *      "patch":{
 *         "tags": ["resource"],
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
   \"location\":{
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
 *               "description":"id of the resource. Devices or Apps using the api key authentication may use the word 'me' to replace their id.",
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
    function ($id) use ($app,$auth) {
		$r = Utils\getResource($auth, $id);
		$data = (array)Utils\getJSON($app);
		
		if(!$auth->hasPermission('resource:admin')){
			// only the resource who create this resource can modify only the data attribute
			$originator = $auth->originator();
			if($originator && ($originator->id() === $r->id() || $originator->id() === $r->createdBy['id'])){
				if( array_keys($data) != array('data') )
					throw new \Exception("access denied. Only the attribute 'data' is allowed.",403);
			}
			else
				throw new \Exception('access denied',403);
		}
		
		if($r->set($data)){
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
 * "/files":{  
 *      "post":{
 *         "tags": ["file"],
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
POST /ething/api/files HTTP/1.1
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
	http://localhost/ething/api/files
```

If the command was successful, a response containing the meta data of the created file will be given back.
You will find in it the id of that file.
This id is a unique string identifying this file and is necessary to make any operation on it.

```json
{
  \"id\":\"73c66-4\",
  \"name\":\"myfile.txt\",
  \"data\":null,
  \"description\":null,
  \"expireAfter\":null,
  \"type\":\"File\",
  \"createdBy\":{
   \"id\":\"56a7B-5\",
   \"type\":\"Device\"
  },
  \"createdDate\":\"2016-01-27T07:46:43+00:00\",
  \"modifiedDate\":\"2016-02-13T10:34:31+00:00\",
  \"mime\":\"text/plain\",
  \"size\":0,
  \"location\":null,
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
$app->post('/files', $auth->permissions('file:write resource:write'),
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
		
		$r = $ething->create('File',$attr,$auth->originator());
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
 * "/files/{id}":{  
 *      "get":{
 *         "tags": ["file"],
 *         "description":"

Retrieves the content of a file.

#### cURL example

The next command show you how to read the content of a file identified by its id.

```bash
curl -H 'X-API-KEY: <YOUR_API_KEY>' http://localhost/ething/api/files/<FILE_ID>
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

$app->get('/files/~/:fn+',  $auth->permissions('file:read resource:read'),
	function ($fn) use ($app,$auth) {
		$route = $app->router()->getNamedRoute('get-files');
		$route->setParams(array('id' => \Utils\getResourceByName($auth,implode('/',$fn),'File')->id()));
		$route->dispatch();
		$app->stop();
	}
);

$app->get('/files/:id', $auth->permissions('file:read resource:read'),
    function ($id) use ($app,$auth) {
		$r = Utils\getResource($auth, $id, 'File');
		$app->lastModified($r->modifiedDate);
		$content = $r->read();
		$app->contentType($r->mime);
		$app->response->headers->set('Content-Length', strlen($content));
		echo $content;
    }
)->name('get-files');

/**
 * @swagger-path
 * "/files/{id}":{  
 *      "put":{
 *         "tags": ["file"],
 *         "description":"
Upload the content of a file.

#### cURL example

The next command show you how to send the content of the local file 'data.txt' into a file.

```bash
curl
	-H 'X-API-KEY: <YOUR_API_KEY>'
	-X PUT
	--data @data.txt
	http://localhost/ething/api/files/<FILE_ID>
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

$app->put('/files/~/:fn+',  $auth->permissions('file:read resource:read'),
	function ($fn) use ($app,$auth,$ething) {
		$filename = implode('/',$fn);
		
		if(!($r = \Utils\getResourceByName($auth,$filename,'File',false))){
			$r = $ething->create('File',array(
				'name' => $filename
			),$auth->originator());
		}
		
		$route = $app->router()->getNamedRoute('put-files');
		$route->setParams(array('id' => $r->id()));
		$route->dispatch();
		$app->stop();
	}
);

$app->put('/files/:id', $auth->permissions('file:write resource:write'),
    function ($id) use ($app,$auth) {
		$r = Utils\getResource($auth, $id, 'File');
		$append = Utils\getParameter('APPEND',Utils\CHK_LOGIC,true,false);
		$bytes = $app->request->getBody();
		
		if(!$append)
			$r->write($bytes);
		else
			$r->append($bytes);
		
		$app->contentType('application/json');
		echo Utils\jsonEncodeFilterByFields($r,Utils\getParameter('fields',Utils\CHK_STRING_ARRAY, true, null));
		
    }
)->name('put-files');

/**
 * @swagger-path
 * "/files/{id}/thumbnail":{  
 *      "get":{
 *         "tags": ["file"],
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
$app->get('/files/:id/thumbnail', $auth->permissions('file:read resource:read'),
    function ($id) use ($app,$auth) {
		$r = Utils\getResource($auth, $id, 'File');
		$app->lastModified($r->modifiedDate);
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
 * "/files/{id}/execute":{  
 *      "get":{
 *         "tags": ["file"],
 *         "description":"Execute a script. Only available for File representing a javascript script.",
 *         "parameters":[  
 *            {  
 *               "name":"id",
 *               "in":"path",
 *               "description":"id of the resource",
 *               "required":true,
 *               "type":"string"
 *            },{  
 *               "name":"args",
 *               "in":"query",
 *               "description":"the arguments to pass to the script",
 *               "required":false,
 *               "type":"string"
 *            }
 *         ],
 *         "responses":{
 *            "200":{
 *               "description":"The result object",
 *               "schema":{
 *                  "type":"object",
 * 	                "properties":{  
 * 	                	"ok":{
 * 	                	   "type":"boolean",
 * 	                	   "description":"True if the script was executed successfully."
 * 	                	},
 * 	                	"return":{
 * 	                	   "type":"object",
 * 	                	   "description":"The return value."
 * 	                	},
 * 	                	"stdout":{
 * 	                	   "type":"string",
 * 	                	   "description":"The stdout output."
 * 	                	},
 * 	                	"stderr":{
 * 	                	   "type":"string",
 * 	                	   "description":"The stderr output."
 * 	                	},
 * 	                	"executionTime":{
 * 	                	   "type":"number",
 * 	                	   "description":"The execution time in seconds."
 * 	                	}
 *                  }
 *               }
 *            }
 *         }
 *      }
 *   }
 */
$app->get('/files/:id/execute', $auth->permissions('file:read resource:read'),
    function ($id) use ($app,$auth,$ething) {
		$r = Utils\getResource($auth, $id, 'File');
		
		if($r->mime === 'application/javascript'){
			
			$args = Utils\getParameter('args',Utils\CHK_STRING, true, null);
			$res = Ething\Script::runFromFile($r, $args);
			
			if(!$res){
				throw new \Utils\Exception('Unable to execute');
			}
			
			$app->contentType('application/json');
			echo json_encode($res,JSON_PRETTY_PRINT|JSON_UNESCAPED_SLASHES);
			
		} else {
			throw new \Utils\Exception('Not executable');
		}
    }
);

/**
 * @swagger-path
 * "/tables":{  
 *      "post":{
 *         "tags": ["table"],
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
	http://localhost/ething/api/tables
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
  \"type\":\"Table\",
  \"createdBy\":null,
  \"createdDate\":\"2016-02-12T14:49:30+00:00\",
  \"modifiedDate\":\"2016-02-15T13:03:20+00:00\",
  \"length\":421,
  \"keys\":{
	 \"temp1\":421,
	 \"temp2\":421
  },
  \"location\":null
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
 *                     "type":"Table",
 *                     "createdBy":{
 *                  	 "id":"56a7B-5",
 *                  	 "type":"Device"
 *                    },
 *                     "createdDate":"2016-02-12T14:49:30+00:00",
 *                     "modifiedDate":"2016-02-15T13:03:20+00:00",
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
$app->post('/tables', $auth->permissions('table:write resource:write'),
    function () use ($app,$auth,$ething) {
		$r = $ething->create('Table',(array)Utils\getJSON($app),$auth->originator());
		if(!$r) throw new \Utils\Exception('Unable to create the table');
		$app->response()->setStatus(201);
		$app->contentType('application/json');
		echo Utils\jsonEncodeFilterByFields($r,Utils\getParameter('fields',Utils\CHK_STRING_ARRAY, true, null));
    }
);

/**
 * @swagger-path
 * "/tables/{id}":{  
 *      "get":{
 *         "tags": ["table"],
 *         "description":"
Retrieves the content of a table.

#### cURL examples

```bash
# get all the data of a table :
curl -H 'X-API-KEY: <YOUR_API_KEY>' http://localhost/ething/api/tables/<TABLE_ID>

# only the first 20 rows :
curl -H 'X-API-KEY: <YOUR_API_KEY>' http://localhost/ething/api/tables/<TABLE_ID>?start=0&length=20

# only the last 20 rows :
curl -H 'X-API-KEY: <YOUR_API_KEY>' http://localhost/ething/api/tables/<TABLE_ID>?start=-20

# only the last 10 rows sorted by the field \"temperature\" in ascending order
# (put a minus before the name of the field if you want to sort in descending order)
curl -H 'X-API-KEY: <YOUR_API_KEY>' http://localhost/ething/api/tables/<TABLE_ID>?start=-10&sort=temperature
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
 *               "enum":["RFC3339","TIMESTAMP","TIMESTAMP_MS","ISO8601","RSS"]
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
$app->get('/tables/~/:fn+',  $auth->permissions('table:read resource:read'),
	function ($fn) use ($app,$auth,$ething) {
		$route = $app->router()->getNamedRoute('get-tables');
		$route->setParams(array('id' => \Utils\getResourceByName($auth,implode('/',$fn),'Table')->id()));
		$route->dispatch();
		$app->stop();
	}
);

$app->get('/tables/:id',  $auth->permissions('table:read resource:read'),
    function ($id) use ($app,$auth) {
		$r = Utils\getResource($auth, $id, 'Table');
		$app->lastModified($r->modifiedDate);
			
		$start = Utils\getParameter('START',Utils\CHK_INT,true,0);
		$length = Utils\getParameter('LENGTH',Utils\CHK_UNSIGNED_INT,true,null);
		$fields = Utils\getParameter('FIELDS',Utils\CHK_STRING_ARRAY,true,null);
		$format = Utils\getParameter('FMT',Utils\CHK_FORMAT,true,Utils\FMT_JSON);
		$sort = Utils\getParameter('SORT',Utils\CHK_STRING,true,null);
		$query = Utils\getParameter('Q',Utils\CHK_STRING,true,null);
		\Ething\Table::$dateFormat = Utils\getParameter('DATEFMT',Utils\CHK_DATEFORMAT,true,\DateTime::RFC3339);
		
		//var_dump(\Ething\Table::$dateFormat); exit;
		$selection = $r->select($start,$length,$fields,$sort,$query);
		
		if($format==Utils\FMT_JSON || $format==Utils\FMT_JSON_PRETTY){
			$app->contentType('application/json');
			echo json_encode($selection, ($format==Utils\FMT_JSON_PRETTY ? JSON_PRETTY_PRINT : 0)|JSON_UNESCAPED_SLASHES);
		}
		else if($format==Utils\FMT_CSV || $format==Utils\FMT_CSV_NOHEADER){
			if(is_null($fields))
				$fields = array_merge(array('id','date'),array_keys($r->keys));
			$app->contentType('text/plain');
			Utils\csv_encode($selection, $fields, $format!=Utils\FMT_CSV_NOHEADER);
		}
    }
)->name('get-tables');

/**
 * @swagger-path
 * "/tables/{id}":{  
 *      "put":{
 *         "tags": ["table"],
 *         "description":"Set the content of a table. The new data will erase the previous one.",
 *         "consumes": ["application/json"],
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

$app->put('/tables/~/:fn+',  $auth->permissions('table:write resource:write'),
	function ($fn) use ($app,$auth,$ething) {
		$filename = implode('/',$fn);
		if(!($r = \Utils\getResourceByName($auth,$filename,'Table',false))){
			$r = $ething->create('Table',array(
				'name' => $filename
			),$auth->originator());
		}
		$route = $app->router()->getNamedRoute('put-tables');
		$route->setParams(array('id' => $r->id()));
		$route->dispatch();
		$app->stop();
	}
);

$app->put('/tables/:id', $auth->permissions('table:write resource:write'),
    function ($id) use ($app,$auth) {
		$r = Utils\getResource($auth, $id, 'Table');
		
		$data = Utils\getJSON($app,true);
		
		$invalidFieldMode = Utils\getParameter('INVALID_FIELD',Utils\CHK_INVALIDFIELDMODE,true,\Ething\Table::INVALID_FIELD_RENAME);
		$skipError = Utils\getParameter('SKIP_ERROR',Utils\CHK_LOGIC,true,true);
		
		if(!empty($data)){
			
			$r->import($data,$invalidFieldMode,$skipError);
			
			$app->contentType('application/json');
			echo Utils\jsonEncodeFilterByFields($r,Utils\getParameter('fields',Utils\CHK_STRING_ARRAY, true, null));
		}
		else {
			throw new \Utils\Exception('No POST data.');
		}
		
    }
)->name('put-tables');


/**
 * @swagger-path
 * "/tables/{id}":{  
 *      "post":{
 *         "tags": ["table"],
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
	http://localhost/ething/api/tables/<TABLE_ID>
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
$app->post('/tables/~/:fn+',  $auth->permissions('table:write resource:write'),
	function ($fn) use ($app,$auth,$ething) {
		$filename = implode('/',$fn);
		if(!($r = \Utils\getResourceByName($auth,$filename,'Table',false))){
			$r = $ething->create('Table',array(
				'name' => $filename
			),$auth->originator());
		}
		$route = $app->router()->getNamedRoute('post-tables');
		$route->setParams(array('id' => $r->id()));
		$route->dispatch();
		$app->stop();
	}
);

$app->post('/tables/:id', $auth->permissions('table:write table:append resource:write'),
    function ($id) use ($app,$auth) {
		$r = Utils\getResource($auth, $id, 'Table');
		
		$data = ($app->request->getMediaType() === 'application/json') ? Utils\getJSON($app,true) : $app->request->post();
		
		$invalidFieldMode = Utils\getParameter('INVALID_FIELD',Utils\CHK_INVALIDFIELDMODE,true,\Ething\Table::INVALID_FIELD_RENAME);
		
		if(!empty($data)){
			$r->insert($data, $invalidFieldMode);
			$app->contentType('application/json');
			echo Utils\jsonEncodeFilterByFields($r,Utils\getParameter('fields',Utils\CHK_STRING_ARRAY, true, null));
		}
		else {
			throw new \Utils\Exception('No POST data.');
		}
		
    }
)->name('post-tables');

/**
 * @swagger-path
 * "/tables/{id}/remove":{  
 *      "post":{
 *         "tags": ["table"],
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
$app->post('/tables/:id/remove', $auth->permissions('table:write resource:write'),
    function ($id) use ($app,$auth) {
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

/**
 * @swagger-path
 * "/tables/{id}/replace":{  
 *      "post":{
 *         "tags": ["table"],
 *         "description":"
Replace the first row that match the query by a new set of data given in the body.
If no row match the query and the upsert flag is set to true, a new row is appended.

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
 *               "name":"q",
 *               "in":"query",
 *               "description":"Query string",
 *               "required":false,
 *               "type":"string"
 *            },
 *            {  
 *               "name":"upsert",
 *               "in":"query",
 *               "description":"If set to true, creates a new row when no row matches the query criteria.",
 *               "required":false,
 *               "default":false,
 *               "type":"boolean"
 *            }
 *         ],
 *         "responses":{
 *            "200":{
 *               "description":"Success",
 *               "schema":{
 *               	"$ref":"#/definitions/Table"
 *               }
 *            }
 *         }
 *      }
 *   }
 */
$app->post('/tables/:id/replace', $auth->permissions('table:write table:append resource:write'),
    function ($id) use ($app,$auth) {
		$r = Utils\getResource($auth, $id, 'Table');
		
		$query = Utils\getParameter('q',Utils\CHK_STRING);
		$data = ($app->request->getMediaType() === 'application/json') ? Utils\getJSON($app,true) : $app->request->post();
		
		$upsert = Utils\getParameter('UPSERT',Utils\CHK_LOGIC,true,false);
		$invalidFieldMode = Utils\getParameter('INVALID_FIELD',Utils\CHK_INVALIDFIELDMODE,true,\Ething\Table::INVALID_FIELD_RENAME);
		
		if(!empty($data)){
			$doc = $r->replaceRow($query, $data, $invalidFieldMode, $upsert);
			
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
 * "/tables/{id}/statistics":{  
 *      "get":{
 *         "tags": ["table"],
 *         "description":"Returns statistics of a specific key (=column)",
 *         "parameters":[  
 *            {  
 *               "name":"id",
 *               "in":"path",
 *               "description":"id of the table",
 *               "required":true,
 *               "type":"string"
 *            },
 *            {
 *               "name":"key",
 *               "in":"query",
 *               "description":"The name of the key (=column).",
 *               "required":true,
 *               "type":"string"
 *            }
 *         ],
 *         "responses":{
 *            "200":{
 *               "description":"The statistics object",
 *               "schema":{
 *                  "type":"object",
 * 	                "properties":{  
 * 	                	"sum":{
 * 	                	   "type":"number",
 * 	                	   "description":"The sum of numeric values."
 * 	                	},
 * 	                	"min":{
 * 	                	   "type":"number",
 * 	                	   "description":"The minimum value."
 * 	                	},
 * 	                	"max":{
 * 	                	   "type":"number",
 * 	                	   "description":"The maximum value."
 * 	                	},
 * 	                	"count":{
 * 	                	   "type":"number",
 * 	                	   "description":"The number of values."
 * 	                	},
 * 	                	"minDate":{
 * 	                	   "type":"date",
 * 	                	   "format":"date-time",
 * 	                	   "description":"The date of the minimum value."
 * 	                	},
 * 	                	"maxDate":{
 * 	                	   "type":"date",
 * 	                	   "format":"date-time",
 * 	                	   "description":"The date of the maximum value."
 * 	                	},
 * 	                	"minId":{
 * 	                	   "type":"string",
 * 	                	   "description":"The id of the minimum value."
 * 	                	},
 * 	                	"maxId":{
 * 	                	   "type":"string",
 * 	                	   "description":"The id of the maximum value."
 * 	                	},
 * 	                	"avg":{
 * 	                	   "type":"number",
 * 	                	   "description":"The average value of the numeric values."
 * 	                	},
 * 	                	"variance":{
 * 	                	   "type":"number",
 * 	                	   "description":"The variance value of the numeric values."
 * 	                	},
 * 	                	"stddev":{
 * 	                	   "type":"number",
 * 	                	   "description":"The standard error value of the numeric values."
 * 	                	},
 * 	                	"startDate":{
 * 	                	   "type":"date",
 * 	                	   "format":"date-time",
 * 	                	   "description":"The date of the oldest value."
 * 	                	},
 * 	                	"endDate":{
 * 	                	   "type":"date",
 * 	                	   "format":"date-time",
 * 	                	   "description":"The date of the newest value."
 * 	                	}
 *                  }
 *               }
 *            }
 *         }
 *      }
 *   }
 */
$app->get('/tables/:id/statistics', $auth->permissions('table:read resource:read'),
    function ($id) use ($app,$auth) {
		$r = Utils\getResource($auth, $id, 'Table');
		
		$key = Utils\getParameter('KEY',Utils\CHK_STRING);
		$query = Utils\getParameter('q',Utils\CHK_STRING, true, null);
				
		$app->contentType('application/json');
		echo json_encode($r->computeStatistics($key, $query),JSON_PRETTY_PRINT|JSON_UNESCAPED_SLASHES|JSON_PARTIAL_OUTPUT_ON_ERROR );
    }
);


// returns a single document in a table

// by id

$app->get('/tables/:id/id/:docId', $auth->permissions('table:read resource:read'),
    function ($id,$docId) use ($app,$auth) {
		$r = Utils\getResource($auth, $id, 'Table');
		$app->lastModified($r->modifiedDate);
		
		Utils\check(Utils\CHK_ID,$docId);
		
		if($doc = $r->getRow($docId)){
			$app->contentType('application/json');
			echo Utils\jsonEncodeFilterByFields($doc,Utils\getParameter('fields',Utils\CHK_STRING_ARRAY, true, null));
		}
		else
			throw new \Utils\Exception('The document does not exist.');
    }
);

$app->delete('/tables/:id/id/:docId', $auth->permissions('table:write resource:write'),
    function ($id,$docId) use ($app,$auth) {
		$r = Utils\getResource($auth, $id, 'Table');
		$app->lastModified($r->modifiedDate);
		
		Utils\check(Utils\CHK_ID,$docId);
		
		$r->remove_rows($docId);
    }
);

$app->patch('/tables/:id/id/:docId', $auth->permissions('table:write resource:write'),
    function ($id,$docId) use ($app,$auth) {
		$r = Utils\getResource($auth, $id, 'Table');
		
		Utils\check(Utils\CHK_ID,$docId);
		
		$data = ($app->request->getMediaType() === 'application/json') ? Utils\getJSON($app,true) : $app->request->post();
		$invalidFieldMode = Utils\getParameter('INVALID_FIELD',Utils\CHK_INVALIDFIELDMODE,true,\Ething\Table::INVALID_FIELD_RENAME);
		
		if(!empty($data)){
			if($doc = $r->replaceRowById($docId, $data, $invalidFieldMode)){
				$app->contentType('application/json');
				echo Utils\jsonEncodeFilterByFields($doc,Utils\getParameter('fields',Utils\CHK_STRING_ARRAY, true, null));
			}
			else
				throw new \Utils\Exception('The document does not exist.');
		}
		else {
			throw new \Utils\Exception('No POST data.');
		}
    }
);

$app->get('/tables/:id/id/:docId/:field', $auth->permissions('table:read resource:read'),
    function ($id,$docId,$field) use ($app,$auth) {
		$r = Utils\getResource($auth, $id, 'Table');
		$app->lastModified($r->modifiedDate);
		
		Utils\check(Utils\CHK_ID,$docId);
		
		if($doc = $r->getRow($docId)){
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

$app->get('/tables/:id/index/:index', $auth->permissions('table:read resource:read'),
    function ($id,$index) use ($app,$auth) {
		$r = Utils\getResource($auth, $id, 'Table');
		$app->lastModified($r->modifiedDate);
		
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

$app->delete('/tables/:id/index/:index', $auth->permissions('table:write resource:write'),
    function ($id,$index) use ($app,$auth) {
		$r = Utils\getResource($auth, $id, 'Table');
		$app->lastModified($r->modifiedDate);
		
		Utils\check(Utils\CHK_INT,$index);
		
		$doc = $r->select($index,1);
		if(count($doc)){
			$doc = $doc[0];
			$r->remove_rows($doc->id);
		}
		else
			throw new \Utils\Exception('Index out of bound.');
		
    }
);

$app->patch('/tables/:id/index/:index', $auth->permissions('table:write resource:write'),
    function ($id,$index) use ($app,$auth) {
		$r = Utils\getResource($auth, $id, 'Table');
		
		Utils\check(Utils\CHK_INT,$index);
		
		$data = ($app->request->getMediaType() === 'application/json') ? Utils\getJSON($app,true) : $app->request->post();
		$invalidFieldMode = Utils\getParameter('INVALID_FIELD',Utils\CHK_INVALIDFIELDMODE,true,\Ething\Table::INVALID_FIELD_RENAME);
		
		if(!empty($data)){
			
			$doc = $r->select($index,1);
			if(count($doc)){
				if($doc = $r->replaceRowById($doc[0]->id, $data, $invalidFieldMode)){
					$app->contentType('application/json');
					echo Utils\jsonEncodeFilterByFields($doc,Utils\getParameter('fields',Utils\CHK_STRING_ARRAY, true, null));
				}
				else
					throw new \Utils\Exception('The document does not exist.');
			}
			else
				throw new \Utils\Exception('Index out of bound.');
		}
		else {
			throw new \Utils\Exception('No POST data.');
		}
    }
);

$app->get('/tables/:id/index/:index/:field', $auth->permissions('table:read resource:read'),
    function ($id,$index,$field) use ($app,$auth) {
		$r = Utils\getResource($auth, $id, 'Table');
		$app->lastModified($r->modifiedDate);
		
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
 * "/apps":{  
 *      "post":{
 *         "tags": ["app"],
 *         "description":"
Creates a new application.

An application consists of a single HTML page. Use the Javascript SDK to easily build an application.

 example:
 
```html
<!DOCTYPE html>
<html>

  <head>

    <!-- CORE -->
    <script src=\"__API_URL__/../lib/core.js\"></script>

  </head>

  <body>

    <!-- your content goes here -->

    <!-- APP -->
    <script type=\"text/javascript\">
      var main = function() {
		var app = EThing.auth.getApp();

        var textnode = document.createTextNode('application : ' + app.name());
        document.body.appendChild(textnode);

      };

      EThing.initialize({
        apiUrl: '__API_URL__',
        apiKey: '__API_KEY__'
      }, main || null, function(error) {
        // on error
        alert(error.message);
      });
      
    </script>

  </body>
</html>
```

#### Preprocessor definitions


The following string are automatically replaced in the HTML code :

| Definition     | Value                                                                |
|----------------|----------------------------------------------------------------------|
| __API_KEY__    | the API key of this application                                      |
| __ID__         | the ID of this application                                           |
| __NAME__       | the name of this application                                         |
| __API_URL__    | the url of this API                                                  |





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
POST /ething/api/apps HTTP/1.1
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
$app->post('/apps', $auth->permissions('app:write resource:write'),
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
		
		
		$r = $ething->create('App',$attr,$auth->originator());
		if(!$r) throw new \Utils\Exception('Unable to create the app');
		$app->response()->setStatus(201);
		$app->contentType('application/json');
		echo Utils\jsonEncodeFilterByFields($r,Utils\getParameter('fields',Utils\CHK_STRING_ARRAY, true, null));
    }
);

/**
 * @swagger-path
 * "/apps/{id}":{  
 *      "get":{
 *         "tags": ["app"],
 *         "description":"Retrieves the script of an application.",
 *         "parameters":[  
 *            {  
 *               "name":"id",
 *               "in":"path",
 *               "description":"id of the resource. Devices or Apps using the api key authentication may use the word 'me' to replace their id.",
 *               "required":true,
 *               "type":"string"
 *            },
 *            {  
 *               "name":"exec",
 *               "in":"query",
 *               "description":"Set this parameter to '1' to get the HTML code ready to be executed in a browser (i.e. content-type set to 'text/html' and the preprocessor definitions set).",
 *               "required":false,
 *               "type":"integer"
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
 *         "description":"Set the script for this application. The script must be a single HTML page.",
 *         "parameters":[  
 *            {  
 *               "name":"id",
 *               "in":"path",
 *               "description":"id of the resource. Devices or Apps using the api key authentication may use the word 'me' to replace their id.",
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
$app->get('/apps/:id', $auth->permissions('app:read app:execute resource:read'),
    function ($id) use ($app,$auth) {
		$r = Utils\getResource($auth, $id, 'App');
		
		if( $execute = ($app->request->get('exec') === '1') ){
			
			// limited to the app:execute permission
			$auth->checkPermission('app:execute');
			$app->lastModified($r->modifiedDate);
			
			$content = $r->readScript();
			
			// replace some SUPER GLOBALS
			$globals = array(
				'__API_URL__' => Utils\hostname() . $app->request->getRootUri(),
				'__API_KEY__' => $r->apikey(),
				'__ID__' => $r->id(),
				'__NAME__' => $r->name()
			);
			
			$app->contentType('text/html');
			echo str_replace(array_keys($globals), array_values($globals), $content);	
			
		}
		else {
			$app->lastModified($r->modifiedDate);
			$app->contentType('text/plain'); // for security reason, will not be executed in browsers
			echo $r->readScript();
		}
    }
);



$app->put('/apps/:id', $auth->permissions('app:write resource:write'),
    function ($id) use ($app,$auth) {
		$r = Utils\getResource($auth, $id, 'App');
		$acceptedMime = array("text/plain","text/html");
		if(!in_array($app->request->getMediaType(),$acceptedMime))
			throw new \Utils\Exception('The script must be one of the following format : '.implode(', ',$acceptedMime));
		$bytes = $app->request->getBody();
		$r->setScript($bytes);
		$app->contentType('application/json');
		echo Utils\jsonEncodeFilterByFields($r,Utils\getParameter('fields',Utils\CHK_STRING_ARRAY, true, null));
    }
);

/**
 * @swagger-path
 * "/apps/{id}/icon":{  
 *      "get":{
 *         "tags": ["app"],
 *         "description":"Retrieves the icon of an application if there is one defined.",
 *         "parameters":[  
 *            {  
 *               "name":"id",
 *               "in":"path",
 *               "description":"id of the resource. Devices or Apps using the api key authentication may use the word 'me' to replace their id.",
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
$app->get('/apps/:id/icon', $auth->permissions('app:read resource:read'),
    function ($id) use ($app,$auth) {
		$r = Utils\getResource($auth, $id, 'App');
		$app->lastModified($r->modifiedDate);
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
 * "/devices":{  
 *      "post":{
 *         "tags": ["device"],
 *         "description":"Creates a new device.",
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
   \"location\":{
      \"latitude\": 5.12,
	  \"longitude\": -45.78
   },
   \"scope\": \"resource:read notification\",
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
 *               	"allOf": [
 *               	  {
 *               	     "type": "object",
 *               	     "required": [
 *               	       "type"
 *               	     ],
 *               	     "properties": {
 *               	       "type": {
 *               	         "type": "string",
 *               	         "description": "The type of the device to create (eg: 'Http' or 'MySensorsEthernetGateway')."
 *               	       }
 *               	     }
 *               	   },
 *               	   {
 *               	     "$ref": "#/definitions/Device"
 *               	   }
 *               	]
 *               }
 *            }
 *         }
 *      }
 *   }
 */
$app->post('/devices', $auth->permissions('device:write resource:write'),
    function () use ($app,$auth,$ething) {
		$data = (array)Utils\getJSON($app);
		
		if(empty($data['type']))
			throw new \Utils\Exception('the type attribute is mandatory');
		
		$type = $data['type'];
		unset($data['type']);
		
		if(!preg_match('@^Device\\\\@', $type)) $type = 'Device\\'.$type;
		
		if(!is_subclass_of('Ething\\'.$type, 'Ething\\Device\\Device'))
			throw new \Utils\Exception("invalid 'type' attribute : {$type}");
		
		// special cases
		switch($type){
			case 'Device\\MySensorsNode':
				if(empty($data['gateway']))
					throw new \Utils\Exception('the gateway attribute is mandatory');
				$gateway = Utils\getResource($auth, $data['gateway'], 'Device\\MySensors.+Gateway');
				unset($data['gateway']);
				
				$r = $gateway->addNode($data);
				break;
			case 'Device\\MySensorsSensor':
				if(empty($data['node']))
					throw new \Utils\Exception('the node attribute is mandatory');
				$node = Utils\getResource($auth, $data['node'], 'Device\\MySensorsNode');
				unset($data['node']);
				
				$r = $node->addSensor($data);
				break;
			default:
				$r = $ething->create($type,$data,$auth->originator());
				break;
		}
		
		if(!$r) throw new \Utils\Exception('Unable to create the device');
		$app->response()->setStatus(201);
		$app->contentType('application/json');
		echo Utils\jsonEncodeFilterByFields($r,Utils\getParameter('fields',Utils\CHK_STRING_ARRAY, true, null));
    }
);




/**
 * @swagger-path
 * "/devices/{id}/api":{  
 *      "get":{
 *         "tags": ["device"],
 *         "description":"Retrieves an object describing the operations available for this device.",
 *         "parameters":[  
 *            {  
 *               "name":"id",
 *               "in":"path",
 *               "description":"id of the resource. Devices or Apps using the api key authentication may use the word 'me' to replace their id.",
 *               "required":true,
 *               "type":"string"
 *            }
 *         ],
 *         "responses":{
 *            "200":{
 *               "description":"object describing the operations available for this device."
 *            }
 *         }
 *      }
 *   }
 */
$app->get('/devices/:id/api', $auth->permissions('device:read resource:read'),
    function ($id) use ($app,$auth) {
		$r = Utils\getResource($auth, $id, 'Device\\.*');
		$app->lastModified($r->modifiedDate);
		
		$app->contentType('application/json');
		echo json_encode($r->operations(),JSON_PRETTY_PRINT|JSON_UNESCAPED_SLASHES);
    }
);

/**
 * @swagger-path
 * "/devices/{id}/api/{operationId}":{  
 *      "get":{
 *         "tags": ["device"],
 *         "description":"Retrieves an object describing the operation identified by operationId.",
 *         "parameters":[  
 *            {  
 *               "name":"id",
 *               "in":"path",
 *               "description":"id of the resource. Devices or Apps using the api key authentication may use the word 'me' to replace their id.",
 *               "required":true,
 *               "type":"string"
 *            },{  
 *               "name":"operationId",
 *               "in":"path",
 *               "description":"id of the operation.",
 *               "required":true,
 *               "type":"string"
 *            }
 *         ],
 *         "responses":{
 *            "200":{
 *               "description":"object describing the operation."
 *            }
 *         }
 *      }
 *   }
 */
$app->get('/devices/:id/api/:operationId', $auth->permissions('device:read resource:read'),
    function ($id, $operationId) use ($app,$auth) {
		$r = Utils\getResource($auth, $id, 'Device\\.*');
		$app->lastModified($r->modifiedDate);
		
		$operation = $r->operation($operationId);
		if(!$operation)
			throw new Exception("unknown operation {$operationId}");
		
		$app->contentType('application/json');
		echo json_encode($operation,JSON_PRETTY_PRINT|JSON_UNESCAPED_SLASHES);
    }
);

/**
 * @swagger-path
 * "/devices/{id}/call/{operationId}":{  
 *      "get":{
 *         "tags": ["device"],
 *         "description":"Execute an operation identified by operationId. The parameters must be passed in the query string.",
 *         "parameters":[  
 *            {  
 *               "name":"id",
 *               "in":"path",
 *               "description":"id of the resource. Devices or Apps using the api key authentication may use the word 'me' to replace their id.",
 *               "required":true,
 *               "type":"string"
 *            },{  
 *               "name":"operationId",
 *               "in":"path",
 *               "description":"id of the operation.",
 *               "required":true,
 *               "type":"string"
 *            },{  
 *               "name":"paramData",
 *               "in":"query",
 *               "description":"required parameters for this operation. Must be json encoded.",
 *               "required":false,
 *               "type":"string"
 *            }
 *         ],
 *         "responses":{
 *            "200":{
 *               "description":"The response of the device."
 *            }
 *         }
 *      }
 *   }
 */
$app->get('/devices/:id/call/:operationId', $auth->permissions('device:write resource:write'),
    function ($id, $operationId) use ($app,$auth) {
		$device = Utils\getResource($auth, $id, 'Device\\.*');
		
		// the data must be json_encoded and passed throught the query parameter "paramData"
		$data = null;
		$paramData = $app->request->get('paramData');
		if($paramData){
			$data = json_decode($jsonStr, true);
			if(json_last_error() !== JSON_ERROR_NONE){
				throw new Exception('Invalid paramData: JSON parse error: '.json_last_error_msg());
			}
		}
		
		ob_implicit_flush(true);
		
		$stream = new \Ething\Stream(null, function($stream, $chunk, $no){
			
			if(!headers_sent()){
				
				$errCode = $stream->errCode();
				http_response_code($errCode === 0 ? 200 : ( $errCode>=100 && $errCode<600 ? $errCode : 400));
				
				$contentType = $stream->contentType();
				if(empty($contentType))
					$contentType = 'application/octet-stream';
				
				header(sprintf("Content-Type: %s", $contentType));
			}
			
			echo $chunk;
			flush();
			
		});
		
		// remove any intermediate cache (Slim created one)
		while(ob_get_level()) ob_end_clean();
		
		$device->call($operationId, $stream, $data, array());
		exit;
		
    }
);

/**
 * @swagger-path
 * "/devices/{id}/call/{operationId}":{  
 *      "post":{
 *         "tags": ["device"],
 *         "description":"Execute an operation identified by operationId. The parameters can either be passed in the query string or in the body as a JSON object or a x-www-form-urlencoded string.",
 *         "parameters":[  
 *            {  
 *               "name":"id",
 *               "in":"path",
 *               "description":"id of the resource. Devices or Apps using the api key authentication may use the word 'me' to replace their id.",
 *               "required":true,
 *               "type":"string"
 *            },{  
 *               "name":"operationId",
 *               "in":"path",
 *               "description":"id of the operation.",
 *               "required":true,
 *               "type":"string"
 *            },{  
 *               "name":"data",
 *               "in":"body",
 *               "description":"required parameters for this operation.",
 *               "required":false,
 *               "schema": {
 *                 "type": "object"
 *               }
 *            }
 *         ],
 *         "responses":{
 *            "200":{
 *               "description":"The response of the device."
 *            }
 *         }
 *      }
 *   }
 */
$app->post('/devices/:id/call/:operationId', $auth->permissions('device:write resource:write'),
    function ($id, $operationId) use ($app,$auth) {
		$device = Utils\getResource($auth, $id, 'Device\\.*');
		
		// the data can either be in the query string or in the post body as a JSON object or a x-www-form-urlencoded string
		$data = $app->request->params();
		try {
			$jsonData = Utils\getJSON($app, true);
			$data = array_merge($data, $jsonData);
		} catch (\Exception $e){}
		
		ob_implicit_flush(true);
		
		$stream = new \Ething\Stream(null, function($stream, $chunk, $no){
			if(!headers_sent()){
				$errCode = $stream->errCode();
				http_response_code($errCode === 0 ? 200 : ( $errCode>=100 && $errCode<600 ? $errCode : 400));
				
				$contentType = $stream->contentType();
				if(empty($contentType))
					$contentType = 'application/octet-stream';
				header(sprintf("Content-Type: %s", $contentType));
			}
			
			echo $chunk;
			flush();
		});
		
		// remove any intermediate cache (Slim created one)
		while(ob_get_level()) ob_end_clean();
		
		$res = $device->call($operationId, $stream, $data, array());
		
		exit;
		
    }
);




/**
 * @swagger-path
 * "/devices/{id}/request/{path}":{  
 *      "get":{
 *         "tags": ["device"],
 *         "summary":"send a GET request to a device.",
 *         "description":"Only available for HTTP device. Forward this HTTP request to a device with the specified path.",
 *         "responses":{
 *           "default":{
 *              "description":"The answer from the device"
 *           }
 *         }
 *      },
 *      "post":{
 *         "tags": ["device"],
 *         "summary":"send a POST request to a device.",
 *         "description":"Only available for HTTP device. Forward this HTTP request to a device with the specified path.",
 *         "responses":{
 *           "default":{
 *              "description":"The answer from the device"
 *           }
 *         }
 *      },
 *      "put":{
 *         "tags": ["device"],
 *         "summary":"send a PUT request to a device.",
 *         "description":"Only available for HTTP device. Forward this HTTP request to a device with the specified path.",
 *         "responses":{
 *           "default":{
 *              "description":"The answer from the device"
 *           }
 *         }
 *      },
 *      "delete":{
 *         "tags": ["device"],
 *         "summary":"send a DELETE request to a device.",
 *         "description":"Only available for HTTP device. Forward this HTTP request to a device with the specified path.",
 *         "responses":{
 *           "default":{
 *              "description":"The answer from the device"
 *           }
 *         }
 *      },
 *      "patch":{
 *         "tags": ["device"],
 *         "summary":"send a PATCH request to a device.",
 *         "description":"Only available for HTTP device. Forward this HTTP request to a device with the specified path.",
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
 *            "description":"id of the resource. Devices or Apps using the api key authentication may use the word 'me' to replace their id.",
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

function processDeviceRequestRoute($id){
	global $app,$auth;
	
	$device = Utils\getResource($auth, $id, 'Device\\Http');
	
	// construct the path
	$args = func_get_args();
	$path = implode('/', (count($args)>1) ? $args[1] : array() );
	
	// build the request from the globals
	$request = \Ething\Request::createFromGlobals();
	// append the current query to the path
	$query = $request->url->query;
	if(!empty($query))
		$path .= '?'.$query;
	
	// send the request
	$device->request($path, $request->getMethod(), $request->getHeaders(), $request->body, true);
	
	die();
}

$app->get('/devices/:id/request(/(:path+))', $auth->permissions('device:read resource:read'), 'processDeviceRequestRoute');
$app->any('/devices/:id/request(/(:path+))', $auth->permissions('device:write resource:write'), 'processDeviceRequestRoute');


/**
 * @swagger-path
 * "/devices/{id}/specification":{  
 *      "get":{
 *         "tags": ["device"],
 *         "description":"Only available for HTTP device. Retrieves the API specification of a device. Only device with an URL set has a Swagger specification",
 *         "parameters":[  
 *            {  
 *               "name":"id",
 *               "in":"path",
 *               "description":"id of the resource. Devices or Apps using the api key authentication may use the word 'me' to replace their id.",
 *               "required":true,
 *               "type":"string"
 *            }
 *         ],
 *         "produces":["application/json"],
 *         "responses":{
 *            "200":{
 *               "description":"The API specification of this device.",
 *               "schema": {
 *               	"type":"file"
 *               }
 *            }
 *         }
 *      }
 *   }
 */
$app->get('/devices/:id/specification', $auth->permissions('device:read resource:read'),
    function ($id) use ($app,$auth) {
		$r = Utils\getResource($auth, $id, 'Device\\Http');
		$app->lastModified($r->modifiedDate);
		$spec = $r->getSpecification();
		$app->contentType('application/json');
		echo json_encode($spec,JSON_PRETTY_PRINT|JSON_UNESCAPED_SLASHES);
    }
);









 
/**
 * @swagger-path
 * "/notification":{  
 *      "post":{
 *         "description":"Send a notification to the registered email addresses (cf. settings).",
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
$app->post('/notification', $auth->permissions('notification'),
    function () use ($app, $ething) {
		$noti = array_merge(array(
			'subject' => null,
			'body' => null
		),Utils\getJSON($app,true));
		$ething->notify($noti['subject'],$noti['body']);
    }
);
 


function processProxyRoute(){
	global $app,$ething;
	
	$url = Utils\getParameter('url',Utils\CHK_URL);
	
	$request = \Ething\Request::createFromGlobals($url);
	

	// auth ?
	$user = null;
	$password = null;
	$mode = null;
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
		}
	}
	
	$proxy = new \Ething\Proxy($ething);
	$proxy->request($request, true, $user, $password, $mode);
	
}

$app->get('/proxy', $auth->permissions('proxy:read'), 'processProxyRoute');
$app->any('/proxy', $auth->permissions('proxy:write'), 'processProxyRoute');













/**
 * @swagger-path
 * "/rules":{  
 *      "get":{
 *         "tags": ["rule"],
 *         "description":"Lists the rules.",
 *         "parameters":[],
 *         "responses":{
 *            "200":{
 *               "description":"A list of rules",
 *               "schema":{
 *                  "type":"array",
 *                  "items":{  
 *                     "$ref":"#/definitions/Rule"
 *                  }
 *               }
 *            }
 *         }
 *      }
 *   }
 */

$app->get('/rules', $auth->permissions('rule:read'),
    function () use ($app,$ething) {
		$app->contentType('application/json');
		echo Utils\jsonEncodeFilterByFields($ething->findRules(),Utils\getParameter('fields',Utils\CHK_STRING_ARRAY, true, null));
    }
);



/**
 * @swagger-path
 * "/rules/{id}":{  
 *      "get":{
 *         "tags": ["rule"],
 *         "description":"
 Returns the attributes of a rule.
 ",
 *         "parameters":[  
 *            {  
 *               "name":"id",
 *               "in":"path",
 *               "description":"id of the rule",
 *               "required":true,
 *               "type":"string"
 *            }
 *         ],
 *         "responses":{
 *            "200":{
 *               "description":"resource object",
 *               "schema":{
 *                  "$ref":"#/definitions/Rule"
 *               }
 *            }
 *         }
 *      }
 *   }
 */
$app->get('/rules/:id', $auth->permissions('rule:read'),
    function ($id) use ($app,$ething) {
		Utils\check(Utils\CHK_ID,$id);
		$rules = $ething->findRules(array(
			'_id' => $id
		));
		if(!count($rules))
			throw new Exception('Unknown rule',404);
		
		$app->contentType('application/json');
		echo Utils\jsonEncodeFilterByFields($rules[0],Utils\getParameter('fields',Utils\CHK_STRING_ARRAY, true, null));
    }
);

/**
 * @swagger-path
 * "/rules/{id}":{  
 *      "delete":{
 *         "tags": ["rule"],
 *         "description":"delete a rule",
 *         "parameters":[  
 *            {  
 *               "name":"id",
 *               "in":"path",
 *               "description":"id of the rule",
 *               "required":true,
 *               "type":"string"
 *            }
 *         ],
 *         "responses":{
 *            "200":{
 *               "description":"the rule has been deleted successfully"
 *            }
 *         }
 *      }
 *   }
 */
$app->delete('/rules/:id', $auth->permissions('rule:admin'),
    function ($id) use ($app,$ething) {
		Utils\check(Utils\CHK_ID,$id);
		$rules = $ething->findRules(array(
			'_id' => $id
		));
		if(!count($rules))
			throw new Exception('Unknown rule',404);
		$rules[0]->remove();
    }
);

/**
 * @swagger-path
 * "/rules/{id}":{  
 *      "patch":{
 *         "tags": ["rule"],
 *         "description":"update a rule. Only properties which are not readonly can be modified.",
 *         "parameters":[  
 *            {  
 *               "name":"id",
 *               "in":"path",
 *               "description":"id of the rule",
 *               "required":true,
 *               "type":"string"
 *            },
 *            {  
 *               "name":"modification",
 *               "in":"body",
 *               "description":"the attributes to modify",
 *               "required":true,
 *               "schema":{
 *                  "$ref":"#/definitions/Rule"
 *               }
 *            }
 *         ],
 *         "responses":{
 *            "200":{
 *               "description":"rule successfully updated",
 *               "schema":{
 *                  "$ref":"#/definitions/Rule"
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
$app->patch('/rules/:id',
    function ($id) use ($app,$ething) {
		
		Utils\check(Utils\CHK_ID,$id);
		$rules = $ething->findRules(array(
			'_id' => $id
		));
		if(!count($rules))
			throw new Exception('Unknown rule',404);
		
		$data = (array)Utils\getJSON($app);
		
		if($rules[0]->set($data)){
			$app->contentType('application/json');
			echo Utils\jsonEncodeFilterByFields($rules[0],Utils\getParameter('fields',Utils\CHK_STRING_ARRAY, true, null));
		}
		else {
			throw new \Utils\Exception('Invalid patch request');
		}
    }
);


/**
 * @swagger-path
 * "/rules":{  
 *      "post":{
 *         "tags": ["rule"],
 *         "description":"

Creates a new rule.

",
 *         "parameters":[  
 *            {  
 *               "name":"attributes",
 *               "in":"body",
 *               "description":"
the metadata of the rule to be created
 ",
 *               "required":true,
 *               "schema":{
 *               	"$ref":"#/definitions/Rule"
 *               }
 *            }
 *         ],
 *         "responses":{
 *            "200":{
 *               "description":"The rule was successfully created",
 *               "schema":{
 *               	"$ref":"#/definitions/Rule"
 *               }
 *            }
 *         }
 *      }
 *   }
 */
$app->post('/rules', $auth->permissions('rule:write'),
    function () use ($app,$ething) {
		
		$attr = (array)Utils\getJSON($app);
		
		$rule = $ething->createRule($attr);
		if(!$rule) throw new \Utils\Exception('Unable to create the rule');
		
		$app->response()->setStatus(201);
		$app->contentType('application/json');
		echo Utils\jsonEncodeFilterByFields($rule,Utils\getParameter('fields',Utils\CHK_STRING_ARRAY, true, null));
		
    }
);



/**
 * @swagger-path
 * "/rules/trigger/{eventName}":{  
 *      "post":{
 *         "tags": ["rule"],
 *         "description":"
Trigger a custom event. The rules which are configured with that event name will be triggered.
",
 *         "parameters":[  
 *            {  
 *               "name":"eventName",
 *               "in":"path",
 *               "description":"the name of the custom event to dispatch",
 *               "required":true,
 *               "type":"string"
 *            }
 *         ],
 *         "responses":{
 *            "200":{
 *               "description":"The event has been dispatched"
 *            }
 *         }
 *      }
 *   }
 */
$app->post('/rules/trigger/:eventName', $auth->permissions('rule:execute'),
    function ($eventName) use ($app,$ething, $auth) {
		$ething->dispatchSignal( Ething\Event\Custom::emit($eventName, $auth->originator()) );
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

$app->error(function (\Exception $e) use ($app,$debug,$ething,$auth) {
	
	$internalerr = $e->getCode() < 100 || $e->getCode() >= 600;
	
	// set the response code
	$responseCode = $internalerr ? 400 : $e->getCode();
	$app->response()->setStatus($responseCode);
	
	// send the error message as JSON
	$app->contentType('application/json');
	
	$ething->log($e, 'HTTP API');
	
	$message = utf8_encode($e->getMessage());
	
	if($debug && $auth->mode() === 'session'){
		$error = array(
			'message' => $message,
			'trace' => $e->getTraceAsString(),
			'line' => $e->getLine(),
			'file' => $e->getFile(),
			'class' => get_class($e),
			'code' => $responseCode
		);
	}
	else {
		$error = array(
			'message' => (!$internalerr) ? $message : 'internal error',
			'code' => $responseCode
		);
	}
	
	echo json_encode($error,JSON_PRETTY_PRINT|JSON_UNESCAPED_SLASHES);
	
});

$app->notFound(function () use ($app) {
	
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
if($ething->config('cors')){
	require_once __DIR__.'/cors.php';
	$app->add(new CorsMiddleware());
	
	\Ething\Proxy::$response_transform = function($proxy){
		$proxy->response->addHeader('Access-Control-Allow-Origin','*');
	};
}




$ething->setDelaySignals(true);

$app->run();




