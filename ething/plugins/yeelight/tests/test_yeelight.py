# coding: utf-8
import pytest
from ..protocol import YeelightProtocol, YeelightAdvertisementProtocol
from ething.core.interfaces import Light
import re


def test_yeelight_controller(core):

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

    assert protocol

    protocol.handle_line(u'{"method": "props", "params": {"power": "on"}}')

    table = device.children(lambda r: r.typeof('resources/Table'))[0]

    print(table)

    assert table
    assert table.length == 1
    assert len(list(table.keys)) == 1

    assert table.select(start=-1)[0].get('state') == True


def test_yeelight_device_color(core):

    data = """Host: 239.255.255.250:1982
Cache-Control: max-age=3600
Location: yeelight://192.168.1.239:55443
NTS: ssdp:alive
Server: POSIX, UPnP/1.0 YGLC/1
id: 0x000000000015243f
model: color
fw_ver: 18
support: get_prop set_default set_power toggle set_bright start_cf stop_cf set_scene
cron_add cron_get cron_del set_ct_abx set_rgb
power: on
bright: 100
color_mode: 2
ct: 4000
rgb: 16711680
hue: 100
sat: 35
name: my_bulb"""

    adv = YeelightAdvertisementProtocol(core)

    dev_info = {
        'ip': '192.168.1.10',
        'port': 80
    }

    for line in data.splitlines():

        matches = re.search('^([^:]+):\s*(.+)\s*$', line)
        if matches:
            value = matches.group(2)
            dev_info[matches.group(1).lower()] = value

    dev = adv.process_device_info(dev_info)

    assert dev
    assert dev.dev_id == '0x000000000015243f'
    assert dev.type == 'resources/YeelightBulbRGBW'


def test_yeelight_device_mono(core):

    data = """Host: 239.255.255.250:1982
Cache-Control: max-age=3600
Location: yeelight://192.168.1.239:55443
NTS: ssdp:alive
Server: POSIX, UPnP/1.0 YGLC/1
id: 0x000000000015243f
model: mono
fw_ver: 18
support: get_prop set_default set_power toggle set_bright start_cf stop_cf set_scene
cron_add cron_get cron_del
power: on
bright: 100
name: my_bulb"""

    adv = YeelightAdvertisementProtocol(core)

    dev_info = {
        'ip': '192.168.1.10',
        'port': 80
    }

    for line in data.splitlines():

        matches = re.search('^([^:]+):\s*(.+)\s*$', line)
        if matches:
            value = matches.group(2)
            dev_info[matches.group(1).lower()] = value

    dev = adv.process_device_info(dev_info)

    assert dev
    assert dev.dev_id == '0x000000000015243f'
    assert dev.type == 'resources/YeelightBulbMono'


def test_yeelight_device_generic(core):

    data = """Host: 239.255.255.250:1982
Cache-Control: max-age=3600
Location: yeelight://192.168.1.239:55443
NTS: ssdp:alive
Server: POSIX, UPnP/1.0 YGLC/1
id: 0x000000000015243f
model: foo
fw_ver: 18
support: get_prop set_default set_power toggle set_bright start_cf stop_cf set_scene
cron_add cron_get cron_del
power: on
bright: 100
name: my_bulb"""

    adv = YeelightAdvertisementProtocol(core)

    dev_info = {
        'ip': '192.168.1.10',
        'port': 80
    }

    for line in data.splitlines():

        matches = re.search('^([^:]+):\s*(.+)\s*$', line)
        if matches:
            value = matches.group(2)
            dev_info[matches.group(1).lower()] = value

    dev = adv.process_device_info(dev_info)

    assert dev
    assert dev.dev_id == '0x000000000015243f'
    assert dev.type == 'resources/YeelightBulbMono'