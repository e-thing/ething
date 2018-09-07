# coding: utf-8
import pytest
from ething.core.core import Core
from ething.core.File import File
from ething.core.Table import Table
from ething.core.Rule import Rule


_core = Core({
    'db': {
        'database': 'test_unit'
    },
    'log': {
        'level': 'debug'
    },
    'debug': True,
    'WebServer': {
        "debug": True,
        'port': 8001
    }
})

@pytest.fixture
def core():
    _core.reset()

    _core.init()

    return _core


