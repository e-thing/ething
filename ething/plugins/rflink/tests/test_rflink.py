# coding: utf-8
import pytest
from .. import RFLinkProtocol
from  ething.core.interfaces import Switch


def test_rflink_controller(core, process):

    gateway = core.create('resources/RFLinkSerialGateway', {
        'name': 'gateway',
        'port': '?'
    })

    assert gateway

    protocol = RFLinkProtocol(gateway)

    protocol.init(process)

    assert protocol

    gateway.inclusion = True

    protocol.handle_line(
        u'20;00;Nodo RadioFrequencyLink - RFLink Gateway V1.1 - R46;')
    assert gateway.version == "1.1"
    assert gateway.revision == "46"

    protocol.handle_line(u'20;06;NewKaku;ID=008440e6;SWITCH=1;CMD=ON;')

    switch = gateway.children(lambda r: r.nodeId == '008440e6')[0]

    assert switch
    assert isinstance(switch, Switch)

    table = switch.children(lambda r: r.isTypeof('resources/Table'))[0]

    print(table)

    assert table
    assert table.length == 1
    assert len(list(table.keys)) == 1

    assert table.select(start=-1)[0].get('state') is True
