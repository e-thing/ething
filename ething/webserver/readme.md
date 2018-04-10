 
The eThing project is an 'Internet of Things' application. Store and retrieve data from devices using HTTP requests.

Access to your resources (file, table, device ...) through HTTP requests.

-------------


### Resource description

There are different types of resources. A resource can either be :

 - file : use this kind of objects to store text data or binary data (image, ...)
 - table : tables are used to store a collection of related data. Table consists of fields and rows.
 - device : this resource describes a device.
 - app : this resource is used to store a HTML/JavaScript script. Use it to handle your data/devices (for instance, you can create an interface to communicate with your device).



### Error messages

When the API returns error messages, it does so in JSON format. For example, an error might look like this:

```json
{
  "message": "The resource does not exist",
  "code" : 404
}
```

The code value correspond to the HTTP status code of the response.


### Authorization

There are several options for authenticating with the API.

#### Basic authentication

HTTP Basic authentication is the simplest way of interacting with the API. 
Simply pass the username (default to 'ething') and password with each request through the `Authorization` header.
This value should be encoded (using base64 encoding) as per the HTTP Basic specification.

```bash
curl -u username:password ...
```


#### API key

Every device or app has an API key. API keys are listed on developer page [http://localhost:8000/client/developer.html](http://localhost:8000/client/developer.html).

API calls authenticated with API key are made on behalf of the Application or Device that own this it ! The permissions can be modified in the resource settings.

Send the following header below on every request :

```
GET /ething/api/resources HTTP/1.1
Host: localhost:8000
X-API-KEY: <YOUR_API_KEY>
```

Here is a cURL example of how to send this header :

```bash
curl -H 'X-API-KEY: <YOUR_API_KEY>' ...
```

You can also simply pass the key as a URL query parameter when making Web service requests. For example:

```bash
curl http://localhost:8000/api/resources?api_key=<YOUR_API_KEY>
```




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
| settings:read  | read the settings                                                    |
| settings:write | modify the settings                                                  |
| rule:read      | read rules attributes                                                |
| rule:write     | create rules                                                         |
| rule:execute   | execute rules                                                        |
| rule:admin     | delete rules                                                         |

### Partial response

By default, the server sends back the full representation of a resource after processing requests.
For better performance, you can ask the server to send only the fields you really need and get a partial response instead.

To request a partial response, use the fields request parameter to specify the fields you want returned.
You can use this parameter with any request that returns response data.

example:

This request will return the meta-data representation containing only the specified keys of a resource

`/resources/56731_a?fields=id,name`


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
 - Date : *RFC 3339* format,  e.g., *2015-03-24T12:00:00+02:00*. Also accept the formats accepted by the [dateparser library](https://github.com/scrapinghub/dateparser).

Constants :

 - 'me' : available only when using API key authentication method. It corresponds to the current Device or App.

 
Examples:

All examples on this page show the unencoded q parameter, where name == 'foobar' is encoded as name+%3d%3d+%27foobar%27.
Client libraries handle this encoding automatically.

Search for resources with the name "foobar"

`name == 'foobar'`

Search for plain text files

`mime == 'text/plain'`

Search for tables resources only

`type == 'Table'`

Search for non empty files or tables

`size > 0 OR length > 0`

Search for resources with the name starting with "foo"

`name ^= 'foobar'`

Search for tables with the extension 'db' or files with the extension 'csv'

`( type == 'Table' AND name $= '.db' ) OR ( type == 'File' AND name $= '.csv' )`

Search for resources modified after Mars 4th 2016

`modifiedDate > '2016-03-04T00:00:00+01:00'`

Search for resources created by the current authenticated Device or App

`createdBy > me`

