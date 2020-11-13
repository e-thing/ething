# coding: utf-8
import pytest
from .. import RFLinkGenericSensor
from ..protocol import RFLinkProtocol
from  ething.interfaces import Relay, Thermometer, HumiditySensor


def test_rflink_controller(core):

    plugin = core.plugins['rflink']

    assert plugin

    protocol = RFLinkProtocol(plugin)

    assert protocol

    plugin.inclusion = True

    protocol.handle_line(
        u'20;00;Nodo RadioFrequencyLink - RFLink Gateway V1.1 - R46;')
    assert plugin.version == "1.1"
    assert plugin.revision == "46"

    # switch/relay
    protocol.handle_line(u'20;06;NewKaku;ID=008440e6;SWITCH=1;CMD=ON;')

    switch = core.find_one(lambda r: r.nodeId == '008440e6')

    assert switch
    assert isinstance(switch, Relay)

    table = switch.children(lambda r: r.typeof('resources/Table'))[0]

    print(table)

    assert table
    assert table.length == 1
    assert len(list(table.keys)) == 1

    assert table.select(start=-1)[0].get('state') is True


    # generic sensor
    protocol.handle_line(u'20;05;Cresta;ID=2801;TEMP=00af;HUM=53;BAT=OK;')

    th_sensor = core.find_one(lambda r: r.nodeId == '2801')

    assert th_sensor

    assert isinstance(th_sensor, RFLinkGenericSensor)
    assert isinstance(th_sensor, Thermometer)
    assert isinstance(th_sensor, HumiditySensor)







