# coding: utf-8
import pytest
import datetime
from ething.db import *


def test_db_store(core):
    store = core.db.store

    store['foo'] = 'bar'

    assert store['foo'] == 'bar'
    assert 'foo' in store

    del store['foo']
    assert 'foo' not in store


def test_db_fs(core):
    fs = core.db.fs

    file = fs.create('toto', version='1.0.0')

    assert fs.exists(file.id)

    assert file.size == 0
    assert file.filename == 'toto'

    assert file['size'] == 0
    assert file['version'] == '1.0.0'

    content = b'hello world'

    file.write(content)

    assert file['size'] == len(content)
    assert file.read() == content

    assert fs.get(file.id) is file

    f2 = fs.create('tata', version='1.0.0')

    assert f2['filename'] == 'tata'
    assert f2['version'] == '1.0.0'


def test_db_table(core):
    db = core.db

    table = db.table_create('toto')

    def init_table(t):
        for i in range(10):
            t.insert({
                'id': i
            })

    init_table(table)

    assert table.length == 10

    assert len(table.select(sort=('id', True), filter_fn=lambda r: r.get('id') < 5)) == 5


    table = db.table_create('foobar')

    table_rows = [{
        'id': 'azerty0',
        'name': 'tata'
    },{
        'id': 'azerty1',
        'name': u'tité',
        'age': 12
    },{
        'id': 'azerty2',
        'name': 'gigu',
        'age': 32,
        'date': datetime.datetime.utcnow()
    }]

    for r in table_rows:
        table.insert(r)

    rows = table.select()

    print(table_rows)
    print(rows)

    assert len(rows) == 3
    assert rows == table_rows

    rows = table.select(length=2)
    assert len(rows) == 2

    rows = table.select(start=1)
    assert len(rows) == 2

    updated_row = table_rows[1].copy()
    updated_row.update({
        'age': 2
    })

    table['azerty1'] = updated_row

    rows = table.select(sort=("age", False))
    assert rows[0]['age'] == 32

    del table['azerty1']

    rows = table.select()
    assert len(rows) == len(table_rows) - 1

    core.db.table_drop('foobar')

    assert not core.db.table_exists('foobar')


def test_db_table_length(core):
    db = core.db

    table = db.table_create('tata')

    def init_table(t):
        for i in range(10):
            t.insert({
                'id': i
            })

    init_table(table)

    table.free()

    assert table.length == 10


def test_db_os(core):
    os = core.db.os

    @attr('name', type="string")
    @uid()
    class F(object):
        pass

    names = ['a', 'b', 'c']
    objs = {}

    for n in names:
        obj = F()
        obj.name = n
        objs[obj.id] = obj
        os.save(obj)

    for idn in objs:
        assert id(os.get(F, idn)) == id(objs[idn])


def test_db_entity(core):

    @db(database=core.db)
    @attr('nickname', type="string")
    @attr('name', type="string")
    @uid()
    class G(object):
        def __init__(self, name, nickname):
            init(self, {
                'name': name,
                'nickname': nickname,
            })
            self.save_cnt = 0
            self.watch_map = {}

        @classmethod
        def __instantiate__(cls, data, data_src, context):
            return cls(data['name'], data['nickname'])

        def __watch__(self, attr, val, old_val):
            if attr.name not in self.watch_map:
                self.watch_map[attr.name] = 0
            self.watch_map[attr.name] += 1

        def __db_save__(self, insert):
            self.save_cnt += 1

    g = G('foo', 'bar')

    assert g.save_cnt == 0

    g.name = 'hello'
    assert g.watch_map['name'] == 1
    assert g.save_cnt == 1

    g.name = 'hello'
    assert g.save_cnt == 1
    g.name = 'hello1'
    assert g.save_cnt == 2
    g.name = 'hello2'
    assert g.save_cnt == 3
    assert g.watch_map['name'] == 3

    save(g)
    assert g.save_cnt == 3


def test_db_link(core):
    @db(database=core.db)
    @attr('name', type="string")
    @uid()
    class J(Entity):
        pass

    j0 = core.db.os.create(J, {'name': 'foo'})
    j1 = core.db.os.create(J, {'name': 'bar'})

    assert core.db.os.get(J, j1.id) is j1

    @attr('j', type=DBLink('J'))
    class K(Entity):
        pass

    k = create(K, {
        'j': j1.id
    })

    assert k.j is j1


def test_cache():

    db = Db(DummyDriver(), auto_commit=True)

    table = db.table_create('toto')

    assert 'toto' in db.table_list()

    assert db.table_exists('toto')

    l = 100

    for i in range(l):
        table.insert({
            'id': i
        })

    assert table.length == l
    assert db['toto'] is table

    # db.commit()
    docs = table.select(sort=('id', False), filter_fn=lambda r: r.get('id') < 5)
    assert docs[0]['id'] == 4

    file = db.fs.create('toto', version='1.0.0')

    file_id = file.id

    assert db.fs.exists(file_id)
    assert file['size'] == 0
    assert file['version'] == '1.0.0'

    content = b'hello world'

    file.write(content)

    assert file['size'] == len(content)
    assert file.read() == content

    assert db.fs.get(file.id) is file

    db.fs.remove(file)

    assert not db.fs.exists(file_id)

    file2 = db.fs.create('tata', version='1.0.0')

    assert file2 in db.fs.list()

    db.clear()

    assert len(db.table_list()) == 0
    assert len(db.fs.list()) == 0