# coding: utf-8
import pytest
from ething.core.Device import *


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

    d.connected = True

    assert d.lastSeenDate is not None

