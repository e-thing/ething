# coding: utf-8
import pytest
from ething.swagger.Reader import Reader
import json
try:
    from urllib.request import urlopen
except ImportError:
    from urllib2 import urlopen


def test_swagger():
    
    def get(url):
        response = urlopen(url)
        return json.loads(response.read().decode("utf-8"))
    
    reader = Reader(get('https://raw.githubusercontent.com/OAI/OpenAPI-Specification/master/examples/v2.0/json/petstore.json'))
    
    
    
