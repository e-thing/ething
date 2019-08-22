# coding: utf-8
import pytest
from ething.utils.jsonpath import jsonpath


def test_create(core):
    data = {
        'payload': {
            'foo': 1
        }
    }

    jsonpath('payload.bar', data, 'set', (2,))
    assert data['payload']['bar'] == 2


def test_delete(core):
    data = {
        'payload': {
            'foo': 1
        }
    }

    jsonpath('payload.foo', data, 'delete')
    assert 'foo' not in data['payload']


