# coding: utf-8
import pytest
from ..HTTP import HTTP


def test_http_request(core):

    device = core.create('resources/HTTP', {
        'name': 'dev',
        'host': 'example.com'
    })

    response = device.make_request("GET", "")

    print(response)

    assert response
