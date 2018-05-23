# coding: utf-8
import pytest
try:
    from urllib.request import urlopen
except ImportError:
    from urllib2 import urlopen

def test_device_http(core):
    
    
    device = core.create('Http', {
        'name': 'dev',
        'url': 'http://localhost'
    })
    
    assert device.type == 'Http'
    
    contents = urlopen("https://raw.githubusercontent.com/OAI/OpenAPI-Specification/master/examples/v2.0/json/petstore.json").read().decode('utf8')
    
    device.setSpecification(contents)
    
    assert len(device.interface.methods) > 0
    
    
    
def test_device_http_interface(core):
    
    device = core.create('Http', {
        'name': 'dev',
        'url': 'http://localhost'
    })
    
    spec = """
{
    "basePath": "/v1",
    "consumes": [
        "application/json"
    ],
    "host": "petstore.swagger.io",
    "swagger": "2.0",
    "produces": [
        "application/json"
    ],
    "definitions": {
        "Pet": {
            "required": [
                "id",
                "name"
            ],
            "properties": {
                "tag": {
                    "type": "string"
                },
                "name": {
                    "type": "string"
                },
                "id": {
                    "type": "integer",
                    "format": "int64"
                }
            }
        },
        "Error": {
            "required": [
                "code",
                "message"
            ],
            "properties": {
                "message": {
                    "type": "string"
                },
                "code": {
                    "type": "integer",
                    "format": "int32"
                }
            }
        },
        "Pets": {
            "type": "array",
            "items": {
                "$ref": "#/definitions/Pet"
            }
        }
    },
    "schemes": [
        "http"
    ],
    "paths": {
        "/pets/{petId}": {
            "get": {
                "tags": [
                    "pets"
                ],
                "responses": {
                    "200": {
                        "description": "Expected response to a valid request",
                        "schema": {
                            "$ref": "#/definitions/Pets"
                        }
                    },
                    "default": {
                        "description": "unexpected error",
                        "schema": {
                            "$ref": "#/definitions/Error"
                        }
                    }
                },
                "operationId": "showPetById",
                "parameters": [
                    {
                        "required": true,
                        "type": "string",
                        "in": "path",
                        "description": "The id of the pet to retrieve",
                        "name": "petId"
                    }
                ],
                "summary": "Info for a specific pet"
            }
        },
        "/pets": {
            "get": {
                "tags": [
                    "pets"
                ],
                "responses": {
                    "200": {
                        "headers": {
                            "x-next": {
                                "type": "string",
                                "description": "A link to the next page of responses"
                            }
                        },
                        "schema": {
                            "$ref": "#/definitions/Pets"
                        },
                        "description": "An paged array of pets"
                    },
                    "default": {
                        "description": "unexpected error",
                        "schema": {
                            "$ref": "#/definitions/Error"
                        }
                    }
                },
                "operationId": "listPets",
                "parameters": [
                    {
                        "required": false,
                        "type": "integer",
                        "description": "How many items to return at one time (max 100)",
                        "in": "query",
                        "format": "int32",
                        "name": "limit"
                    }
                ],
                "summary": "List all pets"
            },
            "post": {
                "tags": [
                    "pets"
                ],
                "responses": {
                    "201": {
                        "description": "Null response"
                    },
                    "default": {
                        "description": "unexpected error",
                        "schema": {
                            "$ref": "#/definitions/Error"
                        }
                    }
                },
                "operationId": "createPets",
                "summary": "Create a pet"
            }
        }
    },
    "info": {
        "license": {
            "name": "MIT"
        },
        "version": "1.0.0",
        "title": "Swagger Petstore"
    }
}
    """
    
    device.setSpecification(spec)
    
    assert hasattr(device, 'createPets')
    assert hasattr(device, 'listPets')
    assert hasattr(device, 'showPetById')
    
    response = device.interface.get_method('listPets').call(10)
    
    print(response)
    
    