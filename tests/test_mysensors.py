# coding: utf-8
import pytest
from ething.mysensors.Message import Message
import ething.mysensors as MySensors
from ething.mysensors.Controller import Controller


def test_mysensors_message():

    m = Message.parse('98;1;1;0;17;269')

    assert m.nodeId == 98
    assert m.childSensorId == 1
    assert m.messageType == MySensors.SET
    assert m.ack == MySensors.NO_ACK
    assert m.subType == MySensors.V_WATT
    assert m.getValue() == 269

    m.setValue(253.4)
    assert m.getValue() == 253.4


def test_mysensors_sensors(core):

    gateway = core.create('MySensorsEthernetGateway', {
        'name': 'gateway',
        'address': '127.0.0.1'
    })

    d = core.create('MySensorsSensor', {
        'name': 'foobar',
        'sensorId': 4,
        'sensorType': 'S_TEMP',
        'data': {
            'temperature': 45,
        },
        'createdBy': gateway
    })

    assert d.interface.is_a('Thermometer')
    assert d.interface.get_method('getTemperature') is not None

    d.sensorType = 'S_RGBW_LIGHT'

    assert d.interface.is_a('Light')


def test_mysensors_controller(core_extended):

    gateway = core_extended.create('MySensorsEthernetGateway', {
        'name': 'gateway',
        'address': '127.0.0.1'
    })

    class Transport(object):
        def __init__(self, controller):
            self.messages = []

        def write(self, message):
            self.messages.append(message)

        def open(self):
            pass

        def close(self):
            pass

    controller = Controller(gateway, Transport)
    controller.open()
    assert gateway.connected

    # test log
    controller.processMessage(b'0;255;3;0;9;foobar')

    # I_GATEWAY_READY
    controller.processMessage(b'0;255;3;0;14;')
    assert controller.gatewayReady

    # I_VERSION
    controller.processMessage(b'0;255;3;0;2;1.0')
    assert controller.gatewayLibVersion == "1.0"

    # I_ID_REQUEST
    controller.processMessage(b'0;255;3;0;3;')
    assert controller.transport.messages[-1].getValue()

    # I_CONFIG
    controller.processMessage(b'0;255;3;0;6;')
    assert controller.transport.messages[-1].subType == MySensors.I_CONFIG
    assert controller.transport.messages[-1].getValue() == "M"

    # node creation
    controller.processMessage(b'12;6;0;0;6;My thermometer')
    controller.processMessage(b'12;6;1;0;0;36.5')

    node = gateway.getNode(12)
    assert node
    sensor = node.getSensor(6)
    assert sensor
    assert sensor.description == 'My thermometer'
    assert sensor.interface.is_a('Thermometer')

    print(sensor.data)

    table = sensor.children({
        'type': 'Table'
    })[0]

    print(table)

    assert table
    assert table.length == 1
    assert len(list(table.keys)) == 1

    assert table.select(start=-1)[0].get('temperature') == 36.5

    # sensor request
    controller.processMessage(b'12;6;2;0;0;')
    assert controller.transport.messages[-1].subType == MySensors.V_TEMP
    assert controller.transport.messages[-1].getValue() == 36.5
