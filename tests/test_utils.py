# coding: utf-8
import pytest
from ething.utils.json import dumps
import json


def test_json():

    obj = {
        'key1': 1,
        'key2': 2,
    }

    assert dumps(obj, sort_keys=True) == json.dumps(obj, sort_keys=True)



