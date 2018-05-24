# coding: utf-8
import pytest
from ething.Helpers import toJson
import json


def test_toJson():

    obj = {
        'key1': 1,
        'key2': 2,
    }

    assert toJson(obj, sort_keys=True) == json.dumps(obj, sort_keys=True)

    obj_ext = obj.copy()
    obj_ext['key3'] = 3

    assert toJson(obj_ext, fields=('key1', 'key2'),
                  sort_keys=True) == json.dumps(obj, sort_keys=True)

    arr = []
    arr_ext = []
    for _ in range(0, 4):
        arr.append(obj.copy())
        arr_ext.append(obj_ext.copy())

    assert toJson(arr, sort_keys=True) == json.dumps(arr, sort_keys=True)
    assert toJson(arr_ext, fields=('key1', 'key2'),
                  sort_keys=True) == json.dumps(arr, sort_keys=True)
