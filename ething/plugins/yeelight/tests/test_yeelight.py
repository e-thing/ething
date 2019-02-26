# coding: utf-8
import pytest
from ..protocol import YeelightProtocol
from ething.core.interfaces import Light


def test_yeelight_controller(core, process):

    device = core.create('resources/YeelightBulbRGBW', {
        'name': 'device',
        'host': '192.168.1.2',
        'model': 'color',
        'fw_ver': '?',
        'dev_id': '?'
    })

    assert device
    assert isinstance(device, Light)

    protocol = YeelightProtocol(device)

    protocol.init(process)

    assert protocol

    protocol.handle_line(u'{"method": "props", "params": {"power": "on"}}')

    table = device.children(lambda r: r.isTypeof('resources/Table'))[0]

    print(table)

    assert table
    assert table.length == 1
    assert len(list(table.keys)) == 1

    assert table.select(start=-1)[0].get('state') == True
