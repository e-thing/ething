# coding: utf-8
import pytest
from ething.mihome.Controller import Controller



def test_mihome_controller(core_extended):
    
    controller = Controller(core_extended)
    
    
    controller.process(r'{"cmd":"report","model":"gateway","sid":"34ce00fb61a9","short_id":0,"data":"{\"rgb\":0,\"illumination\":503}"}', '192.168.1.2')
    
    gateway = core_extended.findOne({
        'sid': '34ce00fb61a9'
    })
    
    assert gateway
    
    assert gateway.interface.is_a('Light')
    
    controller.process(r'{"cmd":"report","model":"weather.v1","sid":"158d0001a4b64a","short_id":22319,"data":"{\"temperature\":\"1983\"}"}')
    
    sensor = core_extended.findOne({
        'sid': '158d0001a4b64a'
    })
    
    assert sensor
    
    assert sensor.interface.is_a('Thermometer')
