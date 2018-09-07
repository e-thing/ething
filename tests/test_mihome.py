# coding: utf-8
import pytest
from ething.plugins.mihome import MihomeProtocol
from ething.core.interfaces import Thermometer, Light


def test_mihome_controller(core, process):

    protocol = MihomeProtocol(core)

    protocol.init(process)

    protocol.data_received(
        (br'{"cmd":"report","model":"gateway","sid":"34ce00fb61a9","short_id":0,"data":"{\"rgb\":0,\"illumination\":503}"}',
         ('192.168.1.2', 9999))
    )

    gateway = core.findOne(lambda r: r.sid == '34ce00fb61a9')

    assert gateway

    assert isinstance(gateway, Light)

    protocol.data_received(
        (
        br'{"cmd":"report","model":"weather.v1","sid":"158d0001a4b64a","short_id":22319,"data":"{\"temperature\":\"1983\"}"}',
        ('192.168.1.2', 9999))
    )

    sensor = core.findOne(lambda r: r.sid == '158d0001a4b64a')

    assert sensor

    assert isinstance(sensor, Thermometer)
