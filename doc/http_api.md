

# EThing HTTP API

**Version**: 0.1.2

## Table of Contents

* [Resource description](#resource-description)
* [Error messages](#error-messages)
* [Authorization](#authorization)
* [Basic authentication](#basic-authentication)
* [API key](#api-key)
* [Scopes](#scopes)
* [Partial response](#partial-response)
* [Filter resource or table data](#filter-resource-or-table-data)
* [Paths](#path)
  * [POST /api/devices](#post-apidevices)
  * [GET /api/devices/{id}/call/{operationId}](#get-apidevicesidcalloperationid)
  * [POST /api/devices/{id}/call/{operationId}](#post-apidevicesidcalloperationid)
  * [POST /api/files](#post-apifiles)
  * [GET /api/files/{id}](#get-apifilesid)
  * [PUT /api/files/{id}](#put-apifilesid)
  * [POST /api/notification](#post-apinotification)
  * [GET /api/resources](#get-apiresources)
  * [DELETE /api/resources/{id}](#delete-apiresourcesid)
  * [GET /api/resources/{id}](#get-apiresourcesid)
  * [PATCH /api/resources/{id}](#patch-apiresourcesid)
  * [POST /api/rules](#post-apirules)
  * [GET /api/settings](#get-apisettings)
  * [PATCH /api/settings](#patch-apisettings)
  * [POST /api/tables](#post-apitables)
  * [GET /api/tables/{id}](#get-apitablesid)
  * [POST /api/tables/{id}](#post-apitablesid)
  * [PUT /api/tables/{id}](#put-apitablesid)
  * [POST /api/tables/{id}/remove](#post-apitablesidremove)
  * [POST /api/tables/{id}/replace](#post-apitablesidreplace)
  * [GET /api/tables/{id}/statistics](#get-apitablesidstatistics)
* [Definitions](#definitions)
  * [Error](#error)
  * [interfaces](#interfaces)
  * [resources](#resources)

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
 - 'location'
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

**Scheme**: http

**Consumes**: application/json

**Produces**: application/json

## Paths

### POST /api/devices

Creates a new device.

#### Request body:

##### Description:

  The metadata of the device to be created.

  example:

  ```json
  {
     "name": "mydevice.txt",
     "location": "room 1",
     "scope": "resource:read notification",
  }
  ```

##### Data:
[Device](#device)

#### Responses:
  - 200: The device was successfully created

### GET /api/devices/{id}/call/{operationId}

Execute an operation identified by operationId. The parameters must be passed in the query string.

#### Path Params:
- **id** [string]: An id representing a Resource.
- **operationId** [string]: id of the operation.

#### Responses:
  - 200: The response of the device.

### POST /api/devices/{id}/call/{operationId}

Execute an operation identified by operationId. The parameters can either be passed in the query string or in the body as a JSON object or a x-www-form-urlencoded string.

#### Path Params:
- **operationId** [string]: id of the operation.
- **id** [string]: An id representing a Resource.

#### Request body:

##### Description:
  required parameters for this operation.

##### Data:
*(object)*

#### Responses:
  - 200: The response of the device.

### POST /api/files

Creates a new file.

There are 2 ways to pass directly the content of the file on the same request :

 - pass the content as a base-64 encoded ASCII string through the key 'content' of the metadata object.

 example:

```json
{
   "name": "myfile.txt",
   "content": "SGVsbG8gd29ybGQgIQ==" // 'Hello world !' in base-64
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
  "name": "image.jpg"
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
    -H "Content-Type: application/json"
    -X POST
    -d '{"name":"myfile.txt"}'
    http://localhost:8000/api/files
```

If the command was successful, a response containing the meta data of the created file will be given back.
You will find in it the id of that file.
This id is a unique string identifying this file and is necessary to make any operation on it.

```json
{
  "id":"73c66-4",
  "name":"myfile.txt",
  "data":null,
  "description":null,
  "expireAfter":null,
  "type":"File",
  "createdBy":{
   "id":"56a7B-5",
   "type":"Device"
  },
  "createdDate":"2016-01-27T07:46:43+00:00",
  "modifiedDate":"2016-02-13T10:34:31+00:00",
  "mime":"text/plain",
  "size":0,
  "location":null,
  "hasThumbnail":false,
  "isText": true
}
```

#### Request body:

##### Description:

  the metadata of the file to be created

  example:

  ```json
  {
     "name": "myfile.txt",
     "description": "an optional description"
  }
  ```

##### Data:
[File](#file)

#### Responses:
  - 200: The file was successfully created
    [File](#file)

### GET /api/files/{id}

Retrieves the content of a file.

#### cURL example

The next command show you how to read the content of a file identified by its id.

```bash
curl -H 'X-API-KEY: <YOUR_API_KEY>' http://localhost:8000/api/files/<FILE_ID>
```

#### Path Params:
- **id** [string]: An id representing a Resource.

#### Responses:
  - 200: The content of this file
    *(file)*

### PUT /api/files/{id}

Upload the content of a file.

#### cURL example

The next command show you how to send the content of the local file 'data.txt' into a file.

```bash
curl
    -H 'X-API-KEY: <YOUR_API_KEY>'
    -X PUT
    --data @data.txt
    http://localhost:8000/api/files/<FILE_ID>
```

#### Path Params:
- **id** [string]: An id representing a Resource.

#### Query Params:
- **append** [boolean]: If true, the content will be appended.

#### Request body:

##### Description:
  The new content. Could be of any type.

##### Data:
*(string)*

#### Responses:
  - 200: The file's metadata
    [File](#file)

### POST /api/notification

Send a notification to the registered email addresses (cf. settings).

#### Request body:

##### Description:
  the data of the notification to be sent

##### Data:
*(object)*
  - **body** *(string)*: the content of the notification
  - **subject** *(string)*: the subject of the notification (default to 'notification')

##### Data:
*(object)*
  - **body** *(string)*
  - **subject** *(string)*

#### Responses:
  - 200: The notification was successfully sent

### GET /api/resources

Lists the resources.

#### cURL example

```bash
curl -H 'X-API-KEY: <YOUR_API_KEY>' http://localhost:8000/api/resources
```

#### Query Params:
- **q** [string]: Query string for searching resources.
- **skip** [integer]: Skips a number of resources.
- **limit** [integer]: Limits the number of resources returned.
- **sort** [string]: The key on which to do the sorting, by default the sort is made by modifiedDate descending. To make the sort descending, prepend the field name by minus "-". For instance, "-createdDate" will sort by createdDate descending.

#### Responses:
  - 200: A list of resources
    *Array*
    items: [Resource](#resource)

### DELETE /api/resources/{id}

deletes a resource

#### Path Params:
- **id** [string]: An id representing a Resource.

#### Query Params:
- **children** [boolean]

#### Responses:
  - 200: the resource has been deleted successfully

### GET /api/resources/{id}

Returns the meta-data of a resource in JSON.

#### Path Params:
- **id** [string]: An id representing a Resource.

#### Responses:
  - 200: resource object
    [Resource](#resource)

### PATCH /api/resources/{id}

update a resource. Only properties which are not readonly can be modified.

Rename a resource :

```json
{
   "name":"myFileRenamed.txt"
}
```

Clear a description :

```json
{
   "description":null
}
```

#### Path Params:
- **id** [string]: An id representing a Resource.

#### Request body:

##### Description:
  the attributes to modify

##### Data:
[Resource](#resource)

#### Responses:
  - 200: resource successfully updated
    [Resource](#resource)

### POST /api/rules

Create a new rule.

#### Request body:

##### Description:

  the metadata of the rule to be created

  example:

  ```json
  {
     "name" : 'myrule',
     "script": "ho58-ju",
     "event": {
         "type": "CustomEvent",
         "name": "foobar"
     }
  }
  ```

##### Data:
[Rule](#rule)

#### Responses:
  - 200: The rule was successfully created
    [Rule](#rule)

### GET /api/settings

Returns the settings

#### Responses:
  - 200: The settings
    *(object)*

### PATCH /api/settings

update your settings.

#### Request body:

##### Description:
  the attributes to modify

##### Data:
*(object)*

#### Responses:
  - 200: settings successfully updated
    *(object)*

### POST /api/tables

Creates a new table.

You may want to pass directly the content of the table in the same request. To do so, just pass the data through the key 'content' of the metadata object;

example:

```json
{
   "name": "foobar.db",
   "content": [
        {
            "temperature": 12.5,
            "pressure": 101325
        }
   ]
}
```

#### cURL example

The next command will create a new table 'mytable.db'.

```bash
curl
    -H 'X-API-KEY: <YOUR_API_KEY>'
    -H "Content-Type: application/json"
    -X POST
    -d '{"name":"mytable.db"}'
    http://localhost:8000/api/tables
```

If the command was successful, a response containing the meta data of the created table will be given back.
You will find in it the id of that table.
This id is a unique string identifying this table and is necessary to make any operation on it.

```json
{
  "id":"56_df0f",
  "name":"mytable.db",
  "data":null,
  "description":null,
  "maxLength":null,
  "expireAfter":null,
  "type":"Table",
  "createdBy":null,
  "createdDate":"2016-02-12T14:49:30+00:00",
  "modifiedDate":"2016-02-15T13:03:20+00:00",
  "length":421,
  "keys":{
     "temp1":421,
     "temp2":421
  },
  "location":null
}
```

#### Request body:

##### Description:

  The metadata of the table to be created.

  example:

  ```json
  {
      "name":"mytable.db"
  }
  ```

##### Data:
[Table](#table)

#### Responses:
  - 200: The table was successfully created
    [Table](#table)

### GET /api/tables/{id}

Retrieves the content of a table.

#### cURL examples

```bash
# get all the data of a table :
curl -H 'X-API-KEY: <YOUR_API_KEY>' http://localhost:8000/api/tables/<TABLE_ID>

# only the first 20 rows :
curl -H 'X-API-KEY: <YOUR_API_KEY>' http://localhost:8000/api/tables/<TABLE_ID>?start=0&length=20

# only the last 20 rows :
curl -H 'X-API-KEY: <YOUR_API_KEY>' http://localhost:8000/api/tables/<TABLE_ID>?start=-20

# only the last 10 rows sorted by the field "temperature" in ascending order
# (put a minus before the name of the field if you want to sort in descending order)
curl -H 'X-API-KEY: <YOUR_API_KEY>' http://localhost:8000/api/tables/<TABLE_ID>?start=-10&sort=temperature
```

#### Path Params:
- **id** [string]: An id representing a Resource.

#### Query Params:
- **sort** [string]: the key on which to do the sorting, by default the sort is made by date ascending. To make the sort descending, prepend the field name by minus "-". For instance, "-date" will sort by date descending.
- **datefmt** [string]: the format of the date field (default to RFC3339) : timestamp,timestamp_ms,rfc3339.
- **fmt** [string]: the output format (default to JSON) : json,json_pretty,csv,csv_no_header.
- **start** [integer]: Position of the first rows to return. If start is negative, the position will start from the end. (default to 0).
- **length** [integer]: Maximum number of rows to return. If not set, returns until the end.
- **q** [string]: Query string for filtering results.

#### Responses:
  - 200: The records of this table
    *Array*
    items: *(object)*
      record's object. Every record has at least the 'id' and 'date' keys.
      - **date** *(string)*: the create date of this record
      - **id** *(string)*: an unique id to identify a record

### POST /api/tables/{id}

Insert a new record in a table

#### Path Params:
- **id** [string]: An id representing a Resource.

#### Query Params:
- **invalid_field** [string]: The behaviour to adopt when an invalid field name appears.

#### Request body:

##### Description:
  The record to be inserted.

  The data must be sent in a JSON formatted object :

  ```json
  {
      "<KEY>":<VALUE>
  }
  ```

  cURL example :

  ```bash
  curl
      -H 'X-API-KEY: <YOUR_API_KEY>'
      -H "Content-Type: application/json"
      -X POST
      -d '{"temperature":15.2, "comment":"outdoor"}'
      http://localhost:8000/api/tables/<TABLE_ID>
  ```

##### Data:
*(object)*

#### Responses:
  - 200: The record was successfully inserted. The table metadata is returned.
    [Table](#table)

### PUT /api/tables/{id}

Set the content of a table. The new data will erase the previous one.

#### Path Params:
- **id** [string]: An id representing a Resource.

#### Query Params:
- **skip_error** [boolean]: Whether to skip data on error or not.
- **invalid_field** [string]: The behaviour to adopt when an invalid field name appears.

#### Request body:

##### Description:
  The content to be inserted as an array of object.

  The data must be sent in a JSON formatted object :

  ```json
  [{
      "<KEY>":<VALUE>
  }]
  ```

  example:

  ```json
  [
      {
        "date": "2016-02-06T15:03:07+01:00",
        "temperature": 12.5,
        "pressure": 101325
      },
      {
        "date": "2016-02-06T16:03:07+01:00",
        "temperature": 13.5,
        "pressure": 101212
      }
  ]
  ```

  If the 'date' field is not present, the current date will be set automatically.
  If an 'id' field is present, it will be automatically be resetted to a new value.

##### Data:
*Array*
items: *(object)*

#### Responses:
  - 200: The content was successfully set. The table metadata is returned.
    [Table](#table)

### POST /api/tables/{id}/remove

Remove one or more records in a table

#### Path Params:
- **id** [string]: An id representing a Resource.

#### Query Params:
- **ids** [string]: The records id to be removed as a comma separated list.

#### Responses:
  - 200: The records was successfully deleted
    [Table](#table)

### POST /api/tables/{id}/replace

Update records in a table

#### Path Params:
- **id** [string]: An id representing a Resource.

#### Query Params:
- **q** [string]: A query that select the rows to update.
- **invalid_field** [string]: The behaviour to adopt when an invalid field name appears.
- **upsert** [boolean]: If true and no records was found, the data will be added to the table as a new record.

#### Responses:
  - 200: The records was successfully updated
    [Table](#table)

### GET /api/tables/{id}/statistics

Compute statistics of a column (=key)

#### Path Params:
- **id** [string]: An id representing a Resource.

#### Query Params:
- **q** [string]: A query string to select the rows used for the statistics computation.
- **key** [string]: the name of the key. Statistics can only be computed for a single key.

#### Responses:
  - 200: The records was successfully updated
    *(object)*
    The statistics object.

## Definitions

### Error

An object describing an error

#### PROPERTIES

  - **code** *(integer)* *(readonly)*: The HTTP response status code
  - **message** *(string)* *(readonly)*: A description of the error

### interfaces

#### Camera

##### INHERITED

[#/interfaces/Interface](##interfacesinterface)

#### Dimmable

##### INHERITED

[#/interfaces/Interface](##interfacesinterface)

##### PROPERTIES

  - **level** *(number)* *(readonly)*: the level of this dimmable switch

#### DimmableLight

##### INHERITED

[#/interfaces/DimmableSwitch](##interfacesdimmableswitch)

#### DimmableSwitch

##### INHERITED

[#/interfaces/Switch](##interfacesswitch)
[#/interfaces/Dimmable](##interfacesdimmable)

#### HumiditySensor

##### INHERITED

[#/interfaces/Interface](##interfacesinterface)

##### PROPERTIES

  - **humidity** *(number)* *(readonly)*: the humidity measured by the sensor in percent.

#### Interface

#### Light

##### INHERITED

[#/interfaces/Switch](##interfacesswitch)

#### LightSensor

##### INHERITED

[#/interfaces/Interface](##interfacesinterface)

##### PROPERTIES

  - **light_level** *(number)* *(readonly)*: the light level measured by the sensor.

#### MoistureSensor

##### INHERITED

[#/interfaces/Interface](##interfacesinterface)

##### PROPERTIES

  - **moisture** *(number)* *(readonly)*: the moisture level measured by this sensor.

#### PressureSensor

##### INHERITED

[#/interfaces/Interface](##interfacesinterface)

##### PROPERTIES

  - **pressure** *(number)* *(readonly)*: the pressure measured by the sensor in Pa.

#### RGBLight

##### INHERITED

[#/interfaces/Light](##interfaceslight)

##### PROPERTIES

  - **color** *(string)* *(readonly)*: the color of the light (#ffffff format)

#### RGBWLight

##### INHERITED

[#/interfaces/RGBLight](##interfacesrgblight)
[#/interfaces/Dimmable](##interfacesdimmable)

#### Switch

##### INHERITED

[#/interfaces/Interface](##interfacesinterface)

##### PROPERTIES

  - **state** *(boolean)* *(readonly)*: the state of the switch

#### Thermometer

##### INHERITED

[#/interfaces/Interface](##interfacesinterface)

##### PROPERTIES

  - **temperature** *(number)* *(readonly)*: the temperature of the sensor

### resources

#### CPUTempDevice

##### INHERITED

[#/resources/Device](##resourcesdevice)
[#/interfaces/Thermometer](##interfacesthermometer)

#### Denon

Denon Device resource representation

##### INHERITED

[#/resources/Device](##resourcesdevice)
[#/interfaces/Switch](##interfacesswitch)

##### PROPERTIES

  - **host**\* *(string)*: The ip address or hostname of the device to connect to.

#### Device

##### INHERITED

[#/resources/Resource](##resourcesresource)

##### PROPERTIES

  - **battery** *(default=null)*: The battery level of this device (must be between 0 (empty) and 100 (full) , or null if the device has no battery information).
  - **connected** *(boolean)* *(default=true)*: Set to true when this device is connected.
  - **interfaces** *(readonly)*: A list of interfaces this device inherit
  - **lastSeenDate** *(readonly)*: The last time this device was reached or made a request.
  - **location** *(default=null)*: The location of this device.
  - **methods** *(readonly)*: The list of the methods available.

#### File

##### INHERITED

[#/resources/Resource](##resourcesresource)

##### PROPERTIES

  - **contentModifiedDate** *(readonly)*: Last time the content of this file was modified (formatted RFC 3339 timestamp).
  - **expireAfter** *(default=null)*: The amount of time (in seconds) after which this resource will be removed.
  - **isText** *(readonly)*: True if this file has text based content.
  - **mime** *(readonly)*: The MIME type of the file (automatically detected from the content).
  - **size** *(readonly)*: The size of this resource in bytes

#### MihomeBase

##### INHERITED

[#/resources/Device](##resourcesdevice)

##### PROPERTIES

  - **model** *(string)* *(readonly)*: The name of the model of the device
  - **short_id** *(readonly)*
  - **sid** *(string)* *(readonly)*: The uniq sid of the device

#### MihomeDevice

Mihome Device base class

##### INHERITED

[#/resources/MihomeBase](##resourcesmihomebase)

##### PROPERTIES

  - **voltage** *(number)* *(readonly)*: the voltage of the battery if any

#### MihomeGateway

##### INHERITED

[#/resources/MihomeBase](##resourcesmihomebase)
[#/interfaces/RGBWLight](##interfacesrgbwlight)
[#/interfaces/LightSensor](##interfaceslightsensor)

##### PROPERTIES

  - **ip**\* *(string)*: The IP address of the gateway
  - **password** *(string)* *(default="")*: The password of the gateway

#### MihomeSensorHT

Mihome temperature/humidity/pressure Sensor Device class.

##### INHERITED

[#/resources/MihomeDevice](##resourcesmihomedevice)
[#/interfaces/Thermometer](##interfacesthermometer)
[#/interfaces/HumiditySensor](##interfaceshumiditysensor)
[#/interfaces/PressureSensor](##interfacespressuresensor)

#### MQTT

MQTT Device resource representation

##### INHERITED

[#/resources/Device](##resourcesdevice)

##### PROPERTIES

  - **auth** *(default=null)*: An object describing the credentials to use.
  - **host**\* *(string)*: The host of the MQTT broker to connect to.
  - **port** *(integer)* *(default=1883)*: The port number of the MQTT broker to connect to.
  - **subscription** *(array)*
    - additionalProperties: False
    - properties: OrderedDict([('name', {'minLength': 1, 'type': 'string'}), ('topic', {'minLength': 1, 'type': 'string'}), ('jsonPath', {'minLength': 1, 'type': 'string'}), ('regexp', {'minLength': 1, 'type': 'string'}), ('xpath', {'minLength': 1, 'type': 'string'})])
    - required: ['name', 'topic']
    - type: object

#### MySensorsBinary

##### INHERITED

[#/resources/MySensorsSensor](##resourcesmysensorssensor)
[#/interfaces/Switch](##interfacesswitch)

#### MySensorsDimmer

##### INHERITED

[#/resources/MySensorsSensor](##resourcesmysensorssensor)
[#/interfaces/DimmableSwitch](##interfacesdimmableswitch)

#### MySensorsEthernetGateway

##### INHERITED

[#/resources/MySensorsGateway](##resourcesmysensorsgateway)

##### PROPERTIES

  - **host**\*: The ip address or hostname of the gateway.
  - **port** *(default=5003)*: The port number of the gateway. The default port number is 5003.

#### MySensorsGateway

see https://www.mysensors.org

##### INHERITED

[#/resources/Device](##resourcesdevice)

##### PROPERTIES

  - **isMetric** *(boolean)* *(default=true)*: Set the unit to Metric(default) instead of Imperial.
  - **libVersion** *(readonly)*: The version of the MySensors library used.

#### MySensorsGenericSensor

##### INHERITED

[#/resources/MySensorsSensor](##resourcesmysensorssensor)

#### MySensorsHumiditySensor

##### INHERITED

[#/resources/MySensorsSensor](##resourcesmysensorssensor)
[#/interfaces/HumiditySensor](##interfaceshumiditysensor)

#### MySensorsNode

MySensorsNode Device resource representation. This device is normally automatically created by a MySensorsGateway instance.

##### INHERITED

[#/resources/Device](##resourcesdevice)

##### PROPERTIES

  - **ackEnabled** *(boolean)* *(default=false)*: If set, every message sent must be acknowledged.
  - **createdBy** *(default=null)*: The id of the resource responsible of the creation of this resource, or null.
  - **firmware** *(readonly)*
  - **libVersion** *(readonly)*: The version of the MySensors library used.
  - **nodeId**\* *(integer)*: The id of the node.
  - **sketchName** *(readonly)*: The name of the sketch uploaded.
  - **sketchVersion** *(readonly)*: The version of the sketch uploaded.
  - **smartSleep** *(boolean)* *(default=false)*: SmartSleep feature enabled for this node.

#### MySensorsPressureSensor

##### INHERITED

[#/resources/MySensorsSensor](##resourcesmysensorssensor)
[#/interfaces/PressureSensor](##interfacespressuresensor)

#### MySensorsRGB

##### INHERITED

[#/resources/MySensorsSensor](##resourcesmysensorssensor)
[#/interfaces/RGBLight](##interfacesrgblight)

#### MySensorsRGBW

##### INHERITED

[#/resources/MySensorsSensor](##resourcesmysensorssensor)
[#/interfaces/RGBWLight](##interfacesrgbwlight)

#### MySensorsSensor

MySensorsSensor Device resource representation. This device is normally automatically created by a MySensorsNode instance.

##### INHERITED

[#/resources/Device](##resourcesdevice)

##### PROPERTIES

  - **createdBy** *(default=null)*: The id of the resource responsible of the creation of this resource, or null.
  - **sensorId**\* *(integer)*: The id of the sensor.
  - **sensorType** *(readonly)*: The type of the sensor.

#### MySensorsSerialGateway

##### INHERITED

[#/resources/MySensorsGateway](##resourcesmysensorsgateway)

##### PROPERTIES

  - **baudrate** *(default=57600)*: The baudrate.
  - **port**\* *(string)*: The serial port name.

#### MySensorsThermometer

##### INHERITED

[#/resources/MySensorsSensor](##resourcesmysensorssensor)
[#/interfaces/Thermometer](##interfacesthermometer)

#### Resource

The base representation of a resource object

##### PROPERTIES

  - **createdBy** *(default=null)*: The id of the resource responsible of the creation of this resource, or null.
  - **createdDate** *(readonly)*: Create time for this resource
  - **data** *(object)* *(default={})*: A collection of arbitrary key-value pairs. Entries with null values are cleared in update. The keys must not be empty or longer than 64 characters, and must contain only the following characters : letters, digits, underscore and dash. Values must be either a string or a boolean or a number

  - **description** *(string)* *(default="")*: A description of this resource.
  - **extends** *(readonly)*: An array of classes this resource is based on.
  - **id** *(readonly)*: The id of the resource
  - **modifiedDate** *(readonly)*: Last time this resource was modified
  - **name**\* *(string)*: The name of the resource
  - **public** *(default=false)*: False: this resource is not publicly accessible. 'readonly': this resource is accessible for reading by anyone. 'readwrite': this resource is accessible for reading and writing by anyone.
  - **type** *(readonly)*: The type of the resource

#### RFLinkGateway

##### INHERITED

[#/resources/Device](##resourcesdevice)

##### PROPERTIES

  - **build** *(readonly)*: The build number of the RFLink library used.
  - **inclusion** *(boolean)* *(default=false)*: If true, new devices will be automatically created.
  - **revision** *(readonly)*: The revision number of the RFLink library used.
  - **version** *(readonly)*: The version of the RFLink library used.

#### RFLinkGenericSensor

##### INHERITED

[#/resources/RFLinkNode](##resourcesrflinknode)

#### RFLinkNode

##### INHERITED

[#/resources/Device](##resourcesdevice)

##### PROPERTIES

  - **createdBy** *(default=null)*: The id of the resource responsible of the creation of this resource, or null.
  - **nodeId** *(string)* *(readonly)*: The hardware id of the node.
  - **protocol** *(string)* *(readonly)*: The protocol name of the node.

#### RFLinkSerialGateway

##### INHERITED

[#/resources/RFLinkGateway](##resourcesrflinkgateway)

##### PROPERTIES

  - **baudrate** *(default=57600)*: The baudrate
  - **port**\* *(string)*: The serial port name.

#### RFLinkSwitch

##### INHERITED

[#/resources/RFLinkNode](##resourcesrflinknode)
[#/interfaces/Switch](##interfacesswitch)

##### PROPERTIES

  - **switchId** *(readonly)*: The switch id of the node. Only available for switch/door/motion subtypes.

#### RTSP

RTSP Device resource representation, usually IP camera.
    avconv must be installed (apt-get install libav-tools)

##### INHERITED

[#/resources/Device](##resourcesdevice)
[#/interfaces/Camera](##interfacescamera)

##### PROPERTIES

  - **transport** *(string)* *(default="tcp")*: Lower transport protocol. Allowed values are the ones defined for the flags for rtsp_transport (see https://libav.org/avconv.html).
  - **url**\* *(string)*: The URL of the device rtsp://... .

#### Rule

Rule dictate the action to perform when an event occurs.
    Rules consist of two parts:
     - The event part specifies the conditions that triggers the invocation of the rule
     - The action part specifies what to execute in response to the event

##### INHERITED

[#/resources/Resource](##resourcesresource)

##### PROPERTIES

  - **actions**\* *(array)*: A list of actions describing a flow. Actions will be executed one after another.
    - [#/actions/Action](##actionsaction)
  - **enabled** *(boolean)* *(default=true)*: If True (default), the rule is enabled
  - **events**\* *(array)*: A list of events describing when to execute this rule.
    - [#/events/Event](##eventsevent)
  - **execution_count** *(readonly)*: The number of times this rule has been executed
  - **execution_date** *(readonly)*: The last time this rule has been executed
  - **scheduler** *(array)* *(default=[])*: Activate this rule only within certain periods of time
    - additionalProperties: False
    - properties: OrderedDict([('start', {'additionalProperties': False, 'required': ['weekDay', 'hour'], 'type': 'object', 'properties': OrderedDict([('weekDay', {'minimum': 0, 'type': 'integer', 'maximum': 6}), ('hour', {'minimum': 0, 'type': 'integer', 'maximum': 24})])}), ('end', {'additionalProperties': False, 'required': ['weekDay', 'hour'], 'type': 'object', 'properties': OrderedDict([('weekDay', {'minimum': 0, 'type': 'integer', 'maximum': 6}), ('hour', {'minimum': 0, 'type': 'integer', 'maximum': 24})])})])
    - required: ['start', 'end']
    - type: object

#### SSH

SSH Device resource representation

##### INHERITED

[#/resources/Device](##resourcesdevice)

##### PROPERTIES

  - **auth**\* *(object)*: An object describing the credentials to use.
    - **password** *(string)*
    - **user** *(string)*
  - **host**\* *(string)*: The ip address or hostname of the device to connect to.
  - **port** *(integer)* *(default=22)*: The port number of the device to connect to. The default port number is 22.

#### Table

##### INHERITED

[#/resources/Resource](##resourcesresource)

##### PROPERTIES

  - **contentModifiedDate** *(readonly)*: Last time the content of this table was modified.
  - **expireAfter** *(default=null)*: The amount of time (in seconds) after which a records will be automatically removed. Set it to null or 0 to disable this feature.
  - **keys** *(object)* *(readonly)*: A key/value object where the keys correspond to the fields available in this table, and the corresponding value is the number of rows where the field is set. __The default keys ('_id' and 'date' are not listed)__

  - **length** *(readonly)*: The number of records in the table
  - **maxLength** *(default=5000)*: The maximum of records allowed in this table. When this number is reached, the oldest records will be removed to insert the new ones (first in, first out). Set it to null or 0 to disable this feature.

#### YeelightBulbRGBW

##### INHERITED

[#/resources/YeelightDevice](##resourcesyeelightdevice)
[#/interfaces/RGBWLight](##interfacesrgbwlight)

##### PROPERTIES

  - **state** *(boolean)* *(readonly)*: the state of the switch

#### YeelightDevice

##### INHERITED

[#/resources/Device](##resourcesdevice)
[#/interfaces/Light](##interfaceslight)

##### PROPERTIES

  - **fw_ver** *(string)* *(readonly)*: The firmware version of the device.
  - **host** *(string)* *(readonly)*: The ip address of the device.
  - **model** *(string)* *(readonly)*: The model of the device.

