# coding: utf-8
import pytest
from ething.yeelight.Controller import Controller



def test_yeelight_controller(core_extended):
    
    
    
    device = core_extended.create('YeelightDevice', {
        'name': 'device',
        'host': '192.168.1.2'
    })
    
    controller = Controller(device)
    
    controller.processMessage({"method":"props","params":{"power":"on"}})
    
    assert device.interface.is_a('Light')
    
    table = device.children({
        'type': 'Table'
    })[0]
    
    print(table)
    
    assert table
    assert table.length == 1
    assert len(list(table.keys)) == 1
    
    assert table.select(start=-1)[0].get('state') == True
    

