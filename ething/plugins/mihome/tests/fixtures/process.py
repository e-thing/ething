# coding: utf-8
import pytest
from ething.core.Process import Process


@pytest.fixture
def process():
    p = Process(name='pytest_process')
    setattr(p, 'transport', None)
    return p


