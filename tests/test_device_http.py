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
    
    
    
    
    
    