# coding: utf-8
from future.utils import string_types
import pytest
from ething.webserver.apikey import generate_apikey, ApikeyManager


def test_apikey_generate():

    key = generate_apikey()

    assert isinstance(key, string_types)
    assert len(key) > 0


def test_manager(core):

    apikey_manager = ApikeyManager(core)

    apikey_manager.clear()

    assert len(apikey_manager.list()) == 0

    apikey = apikey_manager.create({
        'name': 'apikey test'
    })

    print(apikey_manager.list())

    assert len(apikey_manager.list()) == 1

    with apikey:
        apikey.name = 'new name'

    assert apikey_manager.get(apikey.id) == apikey
    assert apikey_manager.find(apikey.value) == apikey

    print(apikey_manager.list())

    apikey.remove()

    assert len(apikey_manager.list()) == 0
