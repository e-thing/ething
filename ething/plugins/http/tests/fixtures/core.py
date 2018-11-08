# coding: utf-8
import pytest
from ething.core import Core


@pytest.fixture
def core():
    _core = Core({
        'db': {
            'database': ':memory:'
        },
        'log': {
            'level': 'DEBUG'
        },
        'debug': True
    })

    _core.init(clear_db=True)

    return _core


