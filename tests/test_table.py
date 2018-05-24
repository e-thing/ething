# coding: utf-8
import pytest
from ething.Table import Table


def test_table_create(core):
    data = [{
        "a": 1,
        "b": False,
        "c": 4.5,
        "d": "string"
    }, {
        "a": 2
    }, {
        "a": 3
    }]

    f = core.create('Table', {
        'name': 'table.tb'
    })

    f.importData(data)

    assert isinstance(f, Table)

    f = core.get(f.id)

    assert isinstance(f, Table)

    assert f.length == len(data)

    assert len(f.select()) == len(data)

    assert len(f.select(query='a>1')) == 2


def test_table_unicode(core):
    data = [{
        "name": u"jean-claude"
    }, {
        "name": u"rémi"
    }]

    f = core.create('Table', {
        'name': 'table.tb'
    })

    f.importData(data)

    assert isinstance(f, Table)

    f = core.get(f.id)

    assert isinstance(f, Table)

    assert f.length == len(data)

    assert len(f.select()) == len(data)

    assert f.select(start=-1)[0].get("name") == data[-1].get("name")

    assert len(f.select(query=u'name == "rémi"')) == 1
