# coding: utf-8
import pytest
from ething.core.Table import Table
from ething.core import Core
import time


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

    f = core.create('resources/Table', {
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

    f = core.create('resources/Table', {
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


def test_benchmark(core):

    f = core.create('resources/Table', {
        'name': 'table.tb'
    })

    start = time.time()

    for _ in range(100):
        f.insert({
            "a": 1,
            "b": False,
            "c": 4.5,
            "d": "string"
        })

    end = time.time()

    print("insertion time: %f s" % ((end - start)/100))

    start = time.time()

    for _ in range(10):
        f.select()

    end = time.time()

    print("select time: %f s" % ((end - start) / 10))


@pytest.mark.parametrize("type,database", [
    ("sqlite", ':memory:'),
    ("sqlite", 'benchmark'),
    ("unqlite", ':memory:'),
    ("unqlite", 'benchmark'),
    ("mongodb", 'benchmark'),
])
def test_benchmark_all(type, database):
    core = Core({
        'db': {
            'database': database,
            'type': type
        }
    })

    core.reset()
    core.init()

    f = core.create('resources/Table', {
        'name': 'table.tb'
    })

    start = time.time()

    for i in range(100):
        f.insert({
            "a": 1,
            "b": False,
            "c": 4.5,
            "d": "string",
            "e": i
        })

    end = time.time()

    print("insertion time: %f s" % ((end - start) / 100))

    start = time.time()

    for _ in range(10):
        f.select()

    end = time.time()

    print("select time: %f s" % ((end - start) / 10))

    start = time.time()

    for _ in range(10):
        f.select(query="e>=50")

    end = time.time()

    print("filter time: %f s" % ((end - start) / 10))