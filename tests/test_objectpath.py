# coding: utf-8
import pytest
from ething.core.utils.ObjectPath import *


def test_objectpath():

    obj = {
        'weather': 'clear sky',
        'id': '4EFmVoW'
    }

    expr = "$.weather is 'clear sky'"

    tree = objectpath.Tree(obj)

    res = tree.execute(expr)

    assert res == True






