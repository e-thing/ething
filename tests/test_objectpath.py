# coding: utf-8
import pytest
from ething.core.utils.ObjectPath import *
import datetime


def test_objectpath():

    obj = {
        'weather': 'clear sky',
        'id': '4EFmVoW'
    }

    expr = "$.weather is 'clear sky'"

    tree = objectpath.Tree(obj)

    res = tree.execute(expr)

    assert res == True

def test_unicode():

    obj = {
        'name': 'rémi'
    }

    expr = u"$.name is 'rémi'"

    tree = objectpath.Tree(obj)

    res = tree.execute(expr)

    assert res == True


def test_date(core):

    obj = {
        'date': datetime.datetime(2019, 2, 10, 12, 0, 0, tzinfo=core.local_tz) # must be offset aware datetime
    }

    expr = "$.date > dateTime('2015-07-04T13:40:04.922Z')"

    res = evaluate(expr, obj)

    assert res == True

    expr = "$.date > dateTime('2025-07-04T13:40:04.922Z')"

    res = evaluate(expr, obj)

    assert res == False

    expr = "$.date > dateTime('1 month ago')"

    res = evaluate(expr, obj)

    assert res == True






