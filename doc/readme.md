

# EThing HTTP API

**Version**: 0.1.0

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
  "message": "The resource does not exist",
  "code" : 404
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
| settings:read  | read the settings                                                |
| settings:write | modify the settings                                              |
| proxy:read     | send GET request through your local network                          |
| proxy:write    | send POST,PUT,PATCH,DELETE through your local network                |
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

### POST /api/apps {#POST--api-apps}

Creates a new application.

An application consists of a single HTML page. Use the Javascript SDK to easily build an application.

 example:

```html
<!DOCTYPE html>
<html>

  <head>

    <!-- CORE -->
    <script src="__JS_URL__"></script>

  </head>

  <body>

    <!-- your content goes here -->

    <!-- APP -->
    <script type="text/javascript">
      var main = function() {
        var app = EThing.auth.getApp();

        var textnode = document.createTextNode('application : ' + app.name());
        document.body.appendChild(textnode);

      };

      EThing.initialize({
        serverUrl: '__SERVER_URL__',
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
| __SERVER_URL__ | the url of the server                                                |
| __JS_URL__     | the url of Javascript API                                            |

There are 2 ways to pass directly the code and the icon data of the application on the same request :

 - pass the code or/and the icon data as a base-64 encoded ASCII string through the key 'content' and 'icon' respectively of the metadata object.

 example:

```json
{
   "name": "myapp",
   "content": "SGVsb...GQgIQ==", // your code in base-64
   "icon": "bXkga...biBkYXRh" // your icon data in base-64
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
  "name": "myapp"
}

--foo_bar_baz
Content-Type: image/jpeg

<JPEG DATA>

--foo_bar_baz
Content-Type: text/html

<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>myapp</title>
</head>
<body>
  Hello World !
</body>
</html>
--foo_bar_baz--
```

#### Query Params:
- **fields** [string]

#### Request body:

##### Description:
  The metadata of the application to be created.

##### Data:
[App](#App)

#### Responses:
  - 200: The application was successfully created
    [App](#App)

### GET /api/apps/{r} {#GET--api-apps-{r}}

Retrieves the script of an application.

#### Query Params:
- **exec** [integer]: Set this parameter to '1' to get the HTML code ready to be executed in a browser (i.e. content-type set to 'text/html' and the preprocessor definitions set).

#### Path Params:
- **r** [string]: An id representing a Resource.

#### Responses:
  - 200: The source code
    *(file)*

### PUT /api/apps/{r} {#PUT--api-apps-{r}}

Set the script for this application. The script must be a single HTML page.

#### Query Params:
- **fields** [string]

#### Path Params:
- **r** [string]: An id representing a Resource.

#### Request body:

##### Description:
  The script as a HTML page.

##### Data:
*(string)*

#### Responses:
  - 200: The script was set successfully. It returns back the meta data of this application.
    [App](#App)

### POST /api/devices {#POST--api-devices}

Creates a new device.

#### Query Params:
- **fields** [string]

#### Request body:

##### Description:

  The metadata of the device to be created.

  example:

  ```json
  {
     "name": "mydevice.txt",
     "location":{
        "latitude": 5.12,
        "longitude": -45.78
     },
     "scope": "resource:read notification",
  }
  ```

##### Data:
[Device](#Device)

#### Responses:
  - 200: The device was successfully created

### GET /api/devices/{r}/api {#GET--api-devices-{r}-api}

Retrieves an object describing the operations available for this device.

#### Path Params:
- **r** [string]: An id representing a Resource.

#### Responses:
  - 200: object describing the operations available for this device.

### GET /api/devices/{r}/api/{operationId} {#GET--api-devices-{r}-api-{operationId}}

Retrieves an object describing the operation identified by operationId.

#### Path Params:
- **operationId** [string]: id of the operation.
- **r** [string]: An id representing a Resource.

#### Responses:
  - 200: object describing the operation.

### GET /api/devices/{r}/call/{operationId} {#GET--api-devices-{r}-call-{operationId}}

Execute an operation identified by operationId. The parameters must be passed in the query string.

#### Path Params:
- **operationId** [string]: id of the operation.
- **r** [string]: An id representing a Resource.

#### Responses:
  - 200: The response of the device.

### POST /api/devices/{r}/call/{operationId} {#POST--api-devices-{r}-call-{operationId}}

Execute an operation identified by operationId. The parameters can either be passed in the query string or in the body as a JSON object or a x-www-form-urlencoded string.

#### Path Params:
- **id** [string]: id of the resource. Devices or Apps using the api key authentication may use the word 'me' to replace their id.
- **operationId** [string]: id of the operation.
- **r** [string]: An id representing a Resource.

#### Request body:

##### Description:
  required parameters for this operation.

##### Data:
*(object)*

#### Responses:
  - 200: The response of the device.

### POST /api/files {#POST--api-files}

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

#### Query Params:
- **fields** [string]

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
[File](#File)

#### Responses:
  - 200: The file was successfully created
    [File](#File)

### GET /api/files/{r} {#GET--api-files-{r}}

Retrieves the content of a file.

#### cURL example

The next command show you how to read the content of a file identified by its id.

```bash
curl -H 'X-API-KEY: <YOUR_API_KEY>' http://localhost:8000/api/files/<FILE_ID>
```

#### Path Params:
- **r** [string]: An id representing a Resource.

#### Responses:
  - 200: The content of this file
    *(file)*

### PUT /api/files/{r} {#PUT--api-files-{r}}

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

#### Query Params:
- **fields** [string]
- **append** [boolean]

#### Path Params:
- **r** [string]: An id representing a Resource.

#### Request body:

##### Description:
  The new content. Could be of any type.

##### Data:
*(string)*

#### Responses:
  - 200: The file's metadata
    [File](#File)

### GET /api/files/{r}/icon {#GET--api-files-{r}-icon}

Retrieves the icon of an application if there is one defined.

#### Path Params:
- **r** [string]: An id representing a Resource.

#### Responses:
  - 200: The icon of this application.
    *(file)*

### POST /api/notification {#POST--api-notification}

Send a notification to the registered email addresses (cf. settings).

#### Query Params:
- **body** [string]
- **subject** [string]

#### Request body:

##### Description:
  the data of the notification to be sent

##### Data:
*(object)*
  - **body** *(string)*: the content of the notification
  - **subject** *(string)*: the subject of the notification (default to 'notification')

#### Responses:
  - 200: The notification was successfully sent

### GET /api/resources {#GET--api-resources}

Lists the resources.

#### cURL example

```bash
curl -H 'X-API-KEY: <YOUR_API_KEY>' http://localhost:8000/api/resources
```

#### Query Params:
- **q** [string]: Query string for searching resources.
- **skip** [integer]: Skips a number of resources.
- **limit** [integer]: Limits the number of resources returned.
- **fields** [string]
- **sort** [string]: The key on which to do the sorting, by default the sort is made by modifiedDate descending. To make the sort descending, prepend the field name by minus "-". For instance, "-createdDate" will sort by createdDate descending.

#### Responses:
  - 200: A list of resources
    *Array*
    items: [Resource](#Resource)

### DELETE /api/resources/{r} {#DELETE--api-resources-{r}}

deletes a resource

#### Query Params:
- **children** [boolean]

#### Path Params:
- **r** [string]: An id representing a Resource.

#### Responses:
  - 200: the resource has been deleted successfully

### GET /api/resources/{r} {#GET--api-resources-{r}}

Returns the meta-data of a resource in JSON.

#### Query Params:
- **fields** [string]

#### Path Params:
- **r** [string]: An id representing a Resource.

#### Responses:
  - 200: resource object
    [Resource](#Resource)

### PATCH /api/resources/{r} {#PATCH--api-resources-{r}}

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

#### Query Params:
- **fields** [string]

#### Path Params:
- **r** [string]: An id representing a Resource.

#### Request body:

##### Description:
  the attributes to modify

##### Data:
[Resource](#Resource)

#### Responses:
  - 200: resource successfully updated
    [Resource](#Resource)

### GET /api/settings {#GET--api-settings}

Returns the settings

#### Responses:
  - 200: The settings
    *(object)*

### PATCH /api/settings {#PATCH--api-settings}

update your settings.

#### Request body:

##### Description:
  the attributes to modify

##### Data:
*(object)*

#### Responses:
  - 200: settings successfully updated
    *(object)*

### POST /api/tables {#POST--api-tables}

Creates a new table.

You may want to pass directly the content of the table in the same request. To do so, just pass the data through the key 'content' of the metadata object;

example:

```json
{
   "name": "matable.db",
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

#### Query Params:
- **fields** [string]

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
[Table](#Table)

#### Responses:
  - 200: The table was successfully created
    [Table](#Table)

### GET /api/tables/{r} {#GET--api-tables-{r}}

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

#### Query Params:
- **sort** [string]: the key on which to do the sorting, by default the sort is made by date ascending. To make the sort descending, prepend the field name by minus "-". For instance, "-date" will sort by date descending.
- **datefmt** [string]: the format of the date field (default to RFC3339).
- **fields** [string]: .
- **fmt** [string]: the output format (default to JSON).
- **start** [integer]: Position of the first rows to return. If start is negative, the position will start from the end. (default to 0).
- **length** [integer]: Maximum number of rows to return. If not set, returns until the end.
- **q** [string]: Query string for filtering results.

#### Path Params:
- **r** [string]: An id representing a Resource.

#### Responses:
  - 200: The records of this table
    *Array*
    items: *(object)*
      record's object. Every record has at least the 'id' and 'date' keys.
      - **date** *(string)*: the create date of this record
      - **id** *(string)*: an unique id to identify a record

### POST /api/tables/{r} {#POST--api-tables-{r}}

Insert a new record in a table

#### Query Params:
- **fields** [string]
- **invalid_field** [string]: The behaviour to adopt when an invalid field name appears.

#### Path Params:
- **r** [string]: An id representing a Resource.

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
    [Table](#Table)

### PUT /api/tables/{r} {#PUT--api-tables-{r}}

Set the content of a table. The new data will erase the previous one.

#### Query Params:
- **skip_error** [boolean]: Whether to skip data on error or not.
- **invalid_field** [string]: The behaviour to adopt when an invalid field name appears.

#### Path Params:
- **r** [string]: An id representing a Resource.

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
    [Table](#Table)

### POST /api/tables/{r}/remove {#POST--api-tables-{r}-remove}

Remove one or more records in a table

#### Query Params:
- **fields** [string]
- **ids** [string]: The records to be removed.

#### Path Params:
- **r** [string]: An id representing a Resource.

#### Responses:
  - 200: The records was successfully deleted
    [Table](#Table)

### POST /api/tables/{r}/replace {#POST--api-tables-{r}-replace}

Update records in a table

#### Query Params:
- **q** [string]: A query that select the rows to update.
- **fields** [string]
- **invalid_field** [string]: The behaviour to adopt when an invalid field name appears.
- **upsert** [boolean]: If true and no records was found, the data will be added to the table as a new record.

#### Path Params:
- **r** [string]: An id representing a Resource.

#### Responses:
  - 200: The records was successfully updated
    [Table](#Table)

### GET /api/tables/{r}/statistics {#GET--api-tables-{r}-statistics}

Compute statistics of a column (=key)

#### Query Params:
- **q** [string]: A query string to select the rows used for the statistics computation.
- **key** [string]: the name of the key. Statistics can only be computed for a single key.

#### Path Params:
- **r** [string]: An id representing a Resource.

#### Responses:
  - 200: The records was successfully updated
    *(object)*
    The statistics object.

## Definitions

### App{#App}

Application resource representation

#### INHERITED

[Resource](#Resource)

#### PROPERTIES

  - **apikey** *(string)*: The apikey for authenticating this app.
  - **contentModifiedDate** *(string)*: Last time the conten of this resource was modified
  - **mime** *(string)*: The mime type of this app
  - **scope** *(string)*: The allowed scopes for this application (space separated list). No permissions by default.
  - **size** *(integer)*: The size of the application in bytes
  - **version** *(string)*: The version of this application

### Device{#Device}

#### INHERITED

[Resource](#Resource)

#### PROPERTIES

  - **battery** *(null)*: The battery level of this device (must be between 0 (empty) and 100 (full) , or null if the device has no battery information).
  - **connected** *(boolean)*: Set to true when this device is connected.
  - **interfaces** *(array)*: A list of intefaces this device inherit

  - **lastSeenDate** *(null)*: Last time this device was reached or made a request.
  - **location** *(null)*: The location of this device.
  - **methods** *(array)*: The list of the methods available.

### Error{#Error}

An object describing an error

#### PROPERTIES

  - **code** *(integer)*: The HTTP response status code
  - **message** *(string)*: A description of the error

### File{#File}

#### INHERITED

[Resource](#Resource)

#### PROPERTIES

  - **contentModifiedDate** *(string)*: Last time the conten of this resource was modified (formatted RFC 3339 timestamp).
  - **expireAfter** *(null)*: The amount of time (in seconds) after which this resource will be removed.
  - **isText** *(boolean)*: True if this file has text based content.
  - **mime** *(string)*: The MIME type of the file (automatically detected from the content).
  - **size** *(integer)*: The size of this resource in bytes

### Http{#Http}

Http Device resource representation

#### INHERITED

[Device](#Device)

#### PROPERTIES

  - **apikey** *(string)*: The apikey for authenticating this device.
  - **auth** *(object)*: An object describing the authentication method to use on HTTP request.
    - **password** *(string)*
    - **type** *(string)*
    - **user** *(string)*

  - **scope** *(string)*: The allowed scopes for this device (space separated list). Restrict the Http api access. Default to an empty string (no access).
  - **url** *(null)*: The URL of the device, or null if there is none defined. No URL defined means that the device cannot be reached. Only device with an URL set has a Swagger specification (see /device/<id>/specification endpoint). The specification object define all the available HTTP requests this device accepts.

### MihomeDevice{#MihomeDevice}

Mihome Device base class

#### INHERITED

[Device](#Device)

#### PROPERTIES

  - **sid**\* *(string)*: The uniq sid of the device

### MihomeGateway{#MihomeGateway}

#### INHERITED

[Device](#Device)

#### PROPERTIES

  - **ip**\* *(string)*: The IP address of the gateway
  - **password** *(string)*: The password of the gateway
  - **sid**\* *(string)*: The uniq sid of the gateway

### MihomeSensorHT{#MihomeSensorHT}

Mihome temperature/humidity/pressure Sensor Device class.

#### INHERITED

[MihomeDevice](#MihomeDevice)

### MQTT{#MQTT}

MQTT Device resource representation

#### INHERITED

[Device](#Device)

#### PROPERTIES

  - **auth** *(null)*: An object describing the credentials to use.
  - **host**\* *(string)*: The host of the MQTT broker to connect to.
  - **port** *(integer)*: The port number of the MQTT broker to connect to.

### MySensorsEthernetGateway{#MySensorsEthernetGateway}

#### INHERITED

[MySensorsGateway](#MySensorsGateway)

#### PROPERTIES

  - **address**\* *(string)*: The ip address or hostname of the gateway.

### MySensorsGateway{#MySensorsGateway}

#### INHERITED

[Device](#Device)

#### PROPERTIES

  - **isMetric** *(boolean)*: Set the unit to Metric(default) instead of Imperial.
  - **libVersion** *(null)*: The version of the MySensors library used.

### MySensorsNode{#MySensorsNode}

MySensorsNode Device resource representation. This device is normally automatically created by a MySensorsGateway instance.

#### INHERITED

[Device](#Device)

#### PROPERTIES

  - **createdBy**\* *(null)*: The id of the resource responsible of the creation of this resource, or null.
  - **firmware** *(null)*
  - **libVersion** *(null)*: The version of the MySensors library used.
  - **nodeId**\* *(integer)*: The id of the node.
  - **sketchName** *(string)*: The name of the sketch uploaded.
  - **sketchVersion** *(string)*: The version of the sketch uploaded.
  - **smartSleep** *(boolean)*: SmartSleep feature enabled for this node.

### MySensorsSensor{#MySensorsSensor}

MySensorsSensor Device resource representation. This device is normally automatically created by a MySensorsNode instance.

#### INHERITED

[Device](#Device)

#### PROPERTIES

  - **createdBy**\* *(null)*: The id of the resource responsible of the creation of this resource, or null.
  - **sensorId**\* *(integer)*: The id of the sensor.
  - **sensorType**\* *(string)*: The type of the sensor.

### MySensorsSerialGateway{#MySensorsSerialGateway}

#### INHERITED

[MySensorsGateway](#MySensorsGateway)

#### PROPERTIES

  - **baudrate** *(integer)*: The baudrate.
  - **port**\* *(string)*: The serial port name.

### Resource{#Resource}

The base representation of a resource object

#### PROPERTIES

  - **createdBy** *(null)*: The id of the resource responsible of the creation of this resource, or null.
  - **createdDate** *(string)*: Create time for this resource
  - **data** *(object)*: A collection of arbitrary key-value pairs. Entries with null values are cleared in update. The keys must not be empty or longer than 64 characters, and must contain only the following characters : letters, digits, underscore and dash. Values must be either a string or a boolean or a number

  - **description** *(string)*: A description of this resource.
  - **extends** *(array)*: An array of classes this resource is based on.

  - **id** *(string)*: The id of the resource
  - **modifiedDate** *(string)*: Last time this resource was modified
  - **name**\* *(string)*: The name of the resource
  - **public**: False: this resource is not publicly accessible. 'readonly': this resource is accessible for reading by anyone. 'readwrite': this resource is accessible for reading and writing by anyone.
  - **type** *(string)*: The type of the resource

### RFLinkGateway{#RFLinkGateway}

#### INHERITED

[Device](#Device)

#### PROPERTIES

  - **build** *(null)*: The build number of the RFLink library used.
  - **revision** *(null)*: The revision number of the RFLink library used.
  - **version** *(null)*: The version of the RFLink library used.

### RFLinkNode{#RFLinkNode}

#### INHERITED

[Device](#Device)

#### PROPERTIES

  - **createdBy**\* *(null)*: The id of the resource responsible of the creation of this resource, or null.
  - **nodeId**\* *(string)*: The hardware id of the node.
  - **protocol**\* *(string)*: The protocol name of the node.
  - **subType**\* *(string)*: The subtype of the device, ie: thermometer, switch, ...
  - **switchId**\* *(null)*: The switch id of the node. Only available for switch/door/motion subtypes.

### RFLinkSerialGateway{#RFLinkSerialGateway}

#### INHERITED

[RFLinkGateway](#RFLinkGateway)

#### PROPERTIES

  - **baudrate** *(integer)*: The baudrate
  - **port**\* *(string)*: The serial port name.

### RTSP{#RTSP}

RTSP Device resource representation, usually IP camera

#### INHERITED

[Device](#Device)

#### PROPERTIES

  - **transport** *(string)*: Lower transport protocol. Allowed values are the ones defined for the flags for rtsp_transport (see https://libav.org/avconv.html).
  - **url**\* *(string)*: The URL of the device rtsp://... .

### SSH{#SSH}

SSH Device resource representation

#### INHERITED

[Device](#Device)

#### PROPERTIES

  - **auth** *(object)*: An object describing the credentials to use.
    - **password** *(string)*
    - **user** *(string)*

  - **host**\* *(string)*: The ip address or hostname of the device to connect to.
  - **port** *(integer)*: The port number of the device to connect to. The default port number is 22.

### Table{#Table}

#### INHERITED

[Resource](#Resource)

#### PROPERTIES

  - **contentModifiedDate** *(string)*: Last time the conten of this resource was modified.
  - **expireAfter** *(null)*: The amount of time (in seconds) after which a records will be automatically removed. Set it to null or 0 to disable this feature.
  - **keys** *(object)*: A key/value object where the keys correspond to the fields available in this table, and the corresponding value is the number of rows where the field is set. __The default keys ('_id' and 'date' are not listed)__

  - **length** *(integer)*: The number of records in the table
  - **maxLength** *(null)*: The maximum of records allowed in this table. When this number is reached, the oldest records will be removed to insert the new ones (first in, first out). Set it to null or 0 to disable this feature.

### YeelightBulbRGBW{#YeelightBulbRGBW}

#### INHERITED

[YeelightDevice](#YeelightDevice)

### YeelightDevice{#YeelightDevice}

#### INHERITED

[Device](#Device)

#### PROPERTIES

  - **host**\* *(string)*: The ip address or hostname of the device to connect to.

### ZigateAqaraTHP{#ZigateAqaraTHP}

Mihome temperatire/humidity/pressure Sensor Device class.

#### INHERITED

[ZigateDevice](#ZigateDevice)

### ZigateDevice{#ZigateDevice}

ZigateDevice Device base class representation

#### INHERITED

[Device](#Device)

#### PROPERTIES

  - **address**\* *(string)*: The short address of this device on the zigbee network
  - **manufacturer**\* *(string)*: The manufacturer of this device
  - **model**\* *(string)*: The model of this device

### ZigateGateway{#ZigateGateway}

#### INHERITED

[Device](#Device)

#### PROPERTIES

  - **appVersion** *(null)*: The version of the Zigate firmware.
  - **sdkVersion** *(null)*: The version of the Zigate SDK.

### ZigateSerialGateway{#ZigateSerialGateway}

#### INHERITED

[ZigateGateway](#ZigateGateway)

#### PROPERTIES

  - **port**\* *(string)*: The serial port name.
