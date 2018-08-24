# coding: utf-8
import pytest
from ething.mysensors.Message import Message
import ething.mysensors as MySensors
from ething.interfaces import Thermometer


def test_mysensors_message():

    m = Message.parse('98;1;1;0;17;269')

    assert m.nodeId == 98
    assert m.childSensorId == 1
    assert m.messageType == MySensors.SET
    assert m.ack == MySensors.NO_ACK
    assert m.subType == MySensors.V_WATT
    assert m.value == 269

    m.value = 253.4
    assert m.value == 253.4


def test_mysensors_thermometer(core):

    gateway = core.create('resources/MySensorsEthernetGateway', {
        'name': 'gateway',
        'host': '127.0.0.1'
    })

    assert gateway

    d = core.create('resources/MySensorsThermometer', {
        'name': 'foobar',
        'sensorId': 4,
        'sensorType': MySensors.S_TEMP,
        'temperature': 45,
        'createdBy': gateway.id
    })

    assert d

    assert isinstance(d, Thermometer)


def test_mysensors_protocol(core, process):

    gateway = core.create('resources/MySensorsEthernetGateway', {
        'name': 'gateway',
        'host': '127.0.0.1'
    })

    assert gateway

    protocol = MySensors.MySensorsProtocol(gateway)

    protocol.init(process)

    assert protocol

    # test log
    protocol.handle_line(u'0;255;3;0;9;foobar')

    # I_GATEWAY_READY
    protocol.handle_line(u'0;255;3;0;14;')
    assert protocol.gatewayReady

    # I_VERSION
    protocol.handle_line(u'0;255;3;0;2;1.0')
    assert protocol.gatewayLibVersion == "1.0"

    # node creation
    protocol.handle_line(u'12;6;0;0;6;My thermometer')
    protocol.handle_line(u'12;6;1;0;0;36.5')

    node = gateway.getNode(12)
    assert node
    sensor = node.getSensor(6)
    assert sensor
    assert sensor.description == 'My thermometer'
    assert isinstance(sensor, Thermometer)

    print(sensor.temperature)

    assert sensor.temperature == 36.5

    table = sensor.children(lambda r: r.isTypeof('resources/Table'))[0]

    print(table)

    assert table
    assert table.length == 1
    assert len(list(table.keys)) == 1

    assert table.select(start=-1)[0].get('temperature') == 36.5

