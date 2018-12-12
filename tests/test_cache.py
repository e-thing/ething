# coding: utf-8
import pytest
from ething.core.database.cache import Db, Dummy_Driver


def test_cache():

    db = Db(Dummy_Driver(), auto_commit=True)

    table = db.create('toto')

    assert 'toto' in db.list_tables()

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

    assert len(db.list_tables()) == 0
    assert len(db.fs.list()) == 0



