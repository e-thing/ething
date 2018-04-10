# coding: utf-8
import pytest



def test_mqtt_controller(core):
    
    device = core.create('MQTT', {
        'name': 'dev',
        'host': 'example.com'
    })
    
    device.setSubscription([
        {
            "topic": "data/json",
            "jsonPath": "$.foo"
        },
        {
            "topic": "data/text",
            "regexp": "^key=(.+)$"
        },
        {
            "topic": "data/xml",
            "xpath": "./foo" # must be relative path !
        }
    ])
    
    device.processPayload(u"data/json", b'{"foo":"bar"}')
    
    table = device.children({
        'type': 'Table',
        'name': 'json'
    })[0]
    
    print(table)
    
    assert table
    assert table.length == 1
    assert len(list(table.keys)) == 1
    
    assert table.select(start=-1)[0].get('value') == "bar"
    
    
    
    
    device.processPayload(u"data/text", b'key=bar')
    
    table = device.children({
        'type': 'Table',
        'name': 'text'
    })[0]
    
    print(table)
    
    assert table
    assert table.length == 1
    assert len(list(table.keys)) == 1
    
    assert table.select(start=-1)[0].get('value') == "bar"
    
    
    
    
    device.processPayload(u"data/xml", b'<data><foo>bar</foo></data>')
    
    
    table = device.children({
        'type': 'Table',
        'name': 'xml'
    })[0]
    
    print(table)
    
    assert table
    assert table.length == 1
    assert len(list(table.keys)) == 1
    
    assert table.select(start=-1)[0].get('value') == "bar"
