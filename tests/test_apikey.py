# coding: utf-8
from future.utils import string_types
import pytest
from ething.core.ApiKey import ApiKey


def test_apikey_generate():

    key = ApiKey.generate()

    assert isinstance(key, string_types)
    assert len(key) > 0
