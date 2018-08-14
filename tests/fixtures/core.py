# coding: utf-8
import pytest
from ething.core import Core
from ething.File import File
from ething.Table import Table
from ething.Rule import Rule


@pytest.fixture
def core():
    core = Core({
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

    core.reset()

    core.init()

    return core


