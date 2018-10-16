# coding: utf-8
import pytest
from ething.core import Core


_core = Core({
    'db': {
        'database': ':memory:'
    },
    'log': {
        'level': 'DEBUG'
    },
    'debug': True
})

@pytest.fixture
def core():
    _core.reset()

    _core.init()

    return _core

