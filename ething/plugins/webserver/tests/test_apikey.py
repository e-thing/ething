# coding: utf-8
from future.utils import string_types
import pytest
from ..apikey import generate_apikey


def test_apikey_generate():

    key = generate_apikey()

    assert isinstance(key, string_types)
    assert len(key) > 0

