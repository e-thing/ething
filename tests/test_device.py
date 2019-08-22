# coding: utf-8
import pytest
from ething.Device import *


def test_device(core):


    class TestDevice(Device):
        pass

    d = core.create('resources/TestDevice', {
        'name': 'test_dev',
        'connected': False
    })

    assert isinstance(d, Device)

    assert d.connected is False
    assert d.lastSeenDate is None

    d.refresh_connect_state(True)

    assert d.connected is True
    assert d.lastSeenDate is not None

