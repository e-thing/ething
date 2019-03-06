

# EThing HTTP API

**Version**: unknown

## Table of Contents

* [Resource description](#resource-description)
* [Error messages](#error-messages)
* [Authorization](#authorization)
* [Basic authentication](#basic-authentication)
* [API key](#api-key)
* [Partial response](#partial-response)
* [Filter resource or table data](#filter-resource-or-table-data)
* [Scopes](#scopes)
* [Paths](#path)
  * [GET /api/devices/{id}/call/{operationId}](#get-apidevicesidcalloperationid)
  * [POST /api/devices/{id}/call/{operationId}](#post-apidevicesidcalloperationid)
  * [GET /api/files/{id}](#get-apifilesid)
  * [PUT /api/files/{id}](#put-apifilesid)
  * [GET /api/resources](#get-apiresources)
  * [POST /api/resources](#post-apiresources)
  * [DELETE /api/resources/{id}](#delete-apiresourcesid)
  * [GET /api/resources/{id}](#get-apiresourcesid)
  * [PATCH /api/resources/{id}](#patch-apiresourcesid)
  * [GET /api/settings](#get-apisettings)
  * [PATCH /api/settings](#patch-apisettings)
  * [GET /api/tables/{id}](#get-apitablesid)
  * [POST /api/tables/{id}](#post-apitablesid)
  * [PUT /api/tables/{id}](#put-apitablesid)
  * [POST /api/tables/{id}/remove](#post-apitablesidremove)
  * [POST /api/tables/{id}/replace](#post-apitablesidreplace)
  * [GET /api/tables/{id}/statistics](#get-apitablesidstatistics)
* [Definitions](#definitions)
  * [Error](#error)
  * [resources](#resources)

## Description

The eThing project is an 'Internet of Things' application. Store and retrieve data from devices using HTTP requests.

Access to your resources (files, tables, devices ...) through HTTP requests.

-------------

### Resource description

There are different types of resources. A resource can either be :

 - file : use this kind of objects to store text data or binary data (image, ...)
 - table : tables are used to store a collection of related data. Table consists of fields and rows.
 - device : this resource describes a device.
 - flow : this resource describes a flow.

### Error messages

When the API returns error messages, it does so in JSON format. For example, an error might look like this:

```json
{
  "message": "The resource does not exist",
  "code" : 404
}
```

The code value correspond to the HTTP status code of the response.

If the server was launched in debug mode, more information is provided.

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

API keys can be generated through the [web interface](http://localhost:8000/#/settings).

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

### Partial response

By default, the server sends back the full representation of a resource after processing requests.
For better performance, you can ask the server to send only the fields you really need and get a partial response instead.

To request a partial response, use the fields request parameter to specify the fields you want returned.
You can use this parameter with any request that returns response data.

example:

This request will return the meta-data representation containing only the specified keys of a resource

`/resources/56731_a?fields=id,name`

### Filter resource or table data

You can search or filter resources or table's rows using a search query based on [ObjectPath query language](http://objectpath.org).

Examples:

Search for resources with the name "foobar"

`$.name is 'foobar'`

Search for plain text files

`$.mime is 'text/plain'`

Search for tables resources only

`$.type is 'resources/Table'`

Search for non empty files or tables

`$.size > 0 or $.length > 0`

Search for resources modified after Mars 4th 2018

`$.modifiedDate > '2018-03-04T00:00:00+01:00'`

### Scopes

Scopes let you specify exactly what type of data access an API key needs.

| Scope          | Description                                                          |
|----------------|----------------------------------------------------------------------|
|   resource:read|                                      read the content of any resource|
|  resource:write|        create resources of any kind or update the resource's metadata|
|       file:read|                                          read the content of any file|
|      file:write|                                        modify the content of any file|
|      table:read|                                         read the content of any table|
|     table:write|                                       modify the content of any table|
|  device:execute|                                              execute a device command|
|   settings:read|                                                     read the settings|
|  settings:write|                                                   modify the settings|
|     flow:inject|                                                inject data into flows|

## Information

**Scheme**: http

**Consumes**: application/json

**Produces**: application/json

## Paths

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

### GET /api/resources

Lists the resources.

#### cURL example

```bash
curl -H 'X-API-KEY: <YOUR_API_KEY>' http://localhost:8000/api/resources
```

#### Query Params:
- **q** [string]: Query string for searching resources.
- **limit** [integer]: Limits the number of resources returned.
- **skip** [integer]: Skips a number of resources.
- **sort** [string]: The key on which to do the sorting, by default the sort is made by modifiedDate descending. To make the sort descending, prepend the field name by minus "-". For instance, "-createdDate" will sort by createdDate descending.

#### Responses:
  - 200: A list of resources

    *Array*
    items: [Resource](#resource)

### POST /api/resources

Creates a new resource.

#### Request body:

##### Description:

  The metadata of the resource to be created.

  example:

  ```json
  {
     "type": "resources/SSH",
     "name": "mydevice",
     "location": "room 1",
     "host": "192.168.1.25"
  }
  ```

##### Data:
[Resource](#resource)

#### Responses:
  - 200: The resource was successfully created

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
- **start** [integer]: Position of the first rows to return. If start is negative, the position will start from the end. (default to 0).
- **length** [integer]: Maximum number of rows to return. If not set, returns until the end.
- **sort** [string]: the key on which to do the sorting, by default the sort is made by date ascending. To make the sort descending, prepend the field name by minus "-". For instance, "-date" will sort by date descending.
- **q** [string]: Query string for filtering results.
- **datefmt** [string]: the format of the date field (default to RFC3339) : timestamp,timestamp_ms,rfc3339.
- **fmt** [string]: the output format (default to JSON) : json,json_pretty,csv,csv_no_header.

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
- **invalid_field** [string]: The behaviour to adopt when an invalid field name appears.
- **skip_error** [boolean]: Whether to skip data on error or not.

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

  - **code** *(integer)*: The HTTP response status code
  - **message** *(string)*: A description of the error

### resources

#### Device

The base class of any device (Switch, light, sensor, controller, ...).

    To register a new Device, simply override the Device class ::

        # optional, for icons naming convention, see https://quasar-framework.org/components/icons.html
        @meta(icon='mdi-play', category='foo')
        # use the `attr` decorator to declare some specific attributes. If history is True, the values are stored in a table. If force_watch is False or not set, only values that differs from the previous one are stored.
        @attr('sensor_value', type=Number(), default=0, mode=READ_ONLY, history=True, force_watch=True, description="sensor value")
        class Foo(Device):

            # (optional) bind some method to the core.scheduler
            @setInterval(30)
            def read(self):
                # this method will be called every 30 seconds during all the lifetime of this instance.
                this.sensor_value = self._read_value_from_the_sensor()

            @method # register this method
            def do_something(self):
                pass

    .. note::
        The registered attributes (using `@attr`) and methods (using `@method`) will be automatically available in the web interface.

    .. note::
        For generic device (sensor, switch, camera, ...) see the interfaces module which list all generic devices.

##### INHERITED

[#/resources/Resource](##resourcesresource)

##### PROPERTIES

  - **battery** *(default=null)*: The battery level of this device (must be between 0 (empty) and 100 (full) , or null if the device has no battery information).
  - **connected** *(boolean)* *(default=true)*: Set to true when this device is connected.
  - **error** *(default=null)*: Any error concerning this device.
  - **lastSeenDate** *(default=null)*: The last time this device was reached or made a request.
  - **location** *(string)* *(default="")*: The location of this device.

#### File

The File resource is used to store data.

    Example::

        f = core.create('resources/File', {
            'name': 'foo.txt'
        })

        f.write('bar', encoding='utf8')

        f.read(encoding='utf8') # = 'bar'

.. attribute:: hasThumbnail

    Return True if this file has a thumbnail.

##### INHERITED

[#/resources/Resource](##resourcesresource)

##### PROPERTIES

  - **contentModifiedDate** *(string)* *(default="2019-03-06T17:12:02.817624+01:00")*: Last time the content of this file was modified (formatted RFC 3339 timestamp).
  - **hasThumbnail**: Return True if this file has a thumbnail.
  - **mime** *(default="text/plain")*: The MIME type of the file (automatically detected from the content or file extension).
  - **size** *(default=0)*: The size of this resource in bytes

#### Flow

The Flow resource represent workflow composed of nodes linked together.

##### INHERITED

[#/resources/Resource](##resourcesresource)

##### PROPERTIES

  - **connections** *(array)* *(default=[])*: A list of connections
    - additionalProperties: False

    - properties: OrderedDict([('src', {'type': 'array', 'items': {'type': 'string', 'minLength': 1}, 'minItems': 2, 'maxItems': 2}), ('dest', {'type': 'array', 'items': {'type': 'string', 'minLength': 1}, 'minItems': 2, 'maxItems': 2})])

    - required: ['src', 'dest']

    - type: object

  - **nodes** *(array)* *(default=[])*: The list of nodes.
    - [#/nodes/Node](##nodesnode)

#### Resource

##### PROPERTIES

  - **createdBy** *(default=null)*: The id of the resource responsible of the creation of this resource, or null.
  - **createdDate** *(string)* *(default="2019-03-06T17:12:02.600755+01:00")*: Create time for this resource
  - **data** *(object)* *(default={})*: A collection of arbitrary key-value pairs.

  - **description** *(string)* *(default="")*: A description of this resource.
  - **extends**: An array of classes this resource is based on.
  - **id** *(string)* *(default="0zgB2qB")*: The id of the resource
  - **modifiedDate** *(string)* *(default="2019-03-06T17:12:02.816627+01:00")*: Last time this resource was modified
  - **name**\* *(string)*: The name of the resource
  - **public** *(default=false)*: False: this resource is not publicly accessible. 'readonly': this resource is accessible for reading by anyone. 'readwrite': this resource is accessible for reading and writing by anyone.
  - **type** *(string)* *(default="resources/Resource")*: The type of the resource

#### Table

The Table resource is used to store time series.

    Example::

        t = core.create('resources/Table', {
            'name': 'foo'
        })

        t.insert({
            'foo': 'bar'
        })

##### INHERITED

[#/resources/Resource](##resourcesresource)

##### PROPERTIES

  - **contentModifiedDate** *(string)* *(default="2019-03-06T17:12:02.817624+01:00")*: Last time the content of this table was modified.
  - **keys** *(object)* *(default={})*: A key/value object where the keys correspond to the fields available in this table, and the corresponding value is the number of rows where the field is set. The default keys ('id' and 'date' are not listed)

  - **length** *(default=0)*: The number of records in the table
  - **maxLength** *(default=5000)*: The maximum of records allowed in this table. When this number is reached, the oldest records will be removed to insert the new ones (first in, first out). Set it to null or 0 to disable this feature.

