 
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

```js
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

```http
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


