# coding: utf-8
import pytest
from ething.Process import Process


@pytest.fixture
def process():
    p = Process('pytest_process')
    setattr(p, 'transport', None)
    return p


