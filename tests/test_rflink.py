# coding: utf-8
import pytest
from ething.rflink.Controller import Controller


def test_rflink_controller(core_extended):

    gateway = core_extended.create('RFLinkSerialGateway', {
        'name': 'gateway',
        'port': '?'
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

    gateway.startInclusion()

    controller.processLine(
        b'20;00;Nodo RadioFrequencyLink - RFLink Gateway V1.1 - R46;')
    assert gateway.version == "1.1"
    assert gateway.revision == "46"

    controller.processLine(b'20;06;NewKaku;ID=008440e6;SWITCH=1;CMD=OFF;')

    switch = gateway.children({
        'nodeId': '008440e6'
    })[0]

    assert switch
    assert switch.interface.is_a('Switch')

    table = switch.children({
        'type': 'Table'
    })[0]

    print(table)

    assert table
    assert table.length == 1
    assert len(list(table.keys)) == 1

    assert table.select(start=-1)[0].get('state') is False
