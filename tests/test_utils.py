# coding: utf-8
import pytest
from ething.core.utils.json import dumps
import json


def test_toJson():

    obj = {
        'key1': 1,
        'key2': 2,
    }

    assert dumps(obj, sort_keys=True) == json.dumps(obj, sort_keys=True)



