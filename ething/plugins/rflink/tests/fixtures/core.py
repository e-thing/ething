# coding: utf-8
import pytest
from ething import Core
from ething import env
import logging


@pytest.fixture
def core():
    env.set_option('rflink', 'port', '?')

    _core = Core(clear_db=True, database=':memory:', plugins=['rflink'], debug=True)

    return _core



