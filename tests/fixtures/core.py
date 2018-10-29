# coding: utf-8
import pytest
from ething.core import Core


_core = Core({
    'db': {
        'database': ':memory:',
        'type': 'sqlite'
    },
    'log': {
        'level': 'DEBUG'
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


