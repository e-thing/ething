# coding: utf-8
import pytest
from ething import Core
import logging


@pytest.fixture
def core():
    _core = Core(clear_db=True, database=':memory:', plugins=['yeelight'], debug=True)

    return _core




