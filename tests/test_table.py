# coding: utf-8
import pytest
from ething.core.Table import Table
from ething.core import Core
import time
import importlib


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


@pytest.mark.parametrize("type,database,module", [
    ("sqlite", ':memory:', 'sqlite3'),
    ("sqlite", 'dbfile', 'sqlite3'),
    ("unqlite", ':memory:', 'unqlite'),
    ("unqlite", 'dbfile', 'unqlite'),
    ("mongodb", 'db', 'pymongo'),
    ("cached_sqlite", ':memory:', 'sqlite3'),
    ("cached_sqlite", 'dbfile', 'sqlite3'),
])
def test_benchmark(type, database, module):

    if module:
        try:
            importlib.import_module(module)
        except ImportError:
            print('module %s not installed, skip test' % module)
            return

    name = '%s:%s' % (type, database)

    core = Core({
        'db': {
            'database': database,
            'type': type
        }
    })

    core.init(clear_db=True)

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

    print("[%s] insertion time: %f s" % (name, (end - start) / 100))

    start = time.time()

    for _ in range(10):
        f.select()

    end = time.time()

    print("[%s] select time: %f s" % (name, (end - start) / 10))

    start = time.time()

    for _ in range(10):
        f.select(query="e>=50")

    end = time.time()

    print("[%s] filter time: %f s" % (name, (end - start) / 10))

    if hasattr(core.db, 'commit'):
        start = time.time()
        core.db.commit()
        end = time.time()
        print("commit time: %f s" % (end - start))