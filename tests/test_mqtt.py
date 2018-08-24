# coding: utf-8
import pytest
from ething.mqtt import MQTT


def test_mqtt_controller(core):

    device = core.create('resources/MQTT', {
        'name': 'dev',
        'host': 'example.com',
        'subscription': [
            {
                "name": "json",
                "topic": "data/json",
                "jsonPath": "$.foo"
            },
            {
                "name": "text",
                "topic": "data/text",
                "regexp": "^key=(.+)$"
            },
            {
                "name": "xml",
                "topic": "data/xml",
                "xpath": "./foo"  # must be relative path !
            }
        ]
    })

    device.processPayload(u"data/json", b'{"foo":"bar"}')

    table = device.children(lambda r: r.isTypeof('resources/Table') and r.name == 'json')[0]

    print(table)

    assert table
    assert table.length == 1
    assert len(list(table.keys)) == 1

    assert table.select(start=-1)[0].get('json') == "bar"

    device.processPayload(u"data/text", b'key=bar')

    table = device.children(lambda r: r.isTypeof('resources/Table') and r.name == 'text')[0]

    print(table)

    assert table
    assert table.length == 1
    assert len(list(table.keys)) == 1

    assert table.select(start=-1)[0].get('text') == "bar"

    device.processPayload(u"data/xml", b'<data><foo>bar</foo></data>')

    table = device.children(lambda r: r.isTypeof('resources/Table') and r.name == 'xml')[0]

    print(table)

    assert table
    assert table.length == 1
    assert len(list(table.keys)) == 1

    assert table.select(start=-1)[0].get('xml') == "bar"
