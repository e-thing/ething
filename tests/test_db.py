# coding: utf-8
import pytest
import datetime


def test_db_kv(core):

    assert core.db.kv_get('foo') is None

    core.db.kv_set('foo', 'bar')

    assert core.db.kv_get('foo') == 'bar'

    assert 'foo' in core.db.kv_list()

    core.db.kv_remove('foo')

    assert core.db.kv_get('foo') is None


def test_db_fs(core):

    content = b'hello world'
    l = len(core.db.listFiles())

    id = core.db.storeFile('fff.txt', content, {
        'attr': 'attrvalue'
    })

    result = core.db.retrieveFile(id)

    assert len(core.db.listFiles()) == l+1

    assert core.db.getFileSize(id) == len(content)

    assert core.db.retrieveFile(id) == content

    assert core.db.getFileMetadata(id).get('attr') == 'attrvalue'

    core.db.removeFile(id)

    assert len(core.db.listFiles()) == l


def test_db_table(core):

    table_name = 'foobar'

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

    core.db.create_table(table_name)

    assert core.db.table_exists(table_name)

    core.db.insert_table_rows(table_name, table_rows)

    rows = core.db.get_table_rows(table_name)

    print(table_rows)
    print(rows)

    assert len(rows) == 3
    assert rows == table_rows

    rows = core.db.get_table_rows(table_name, query = "age > 10")
    assert len(rows) == 2

    updated_row = table_rows[1].copy()
    updated_row.update({
        'age': 2
    })
    old_row = core.db.update_table_row(table_name, 'azerty1', updated_row, True)
    assert old_row == table_rows[1]

    rows = core.db.get_table_rows(table_name, query="age > 10")
    assert len(rows) == 1

    core.db.remove_table_row(table_name, 'azerty1', True)

    rows = core.db.get_table_rows(table_name)
    assert len(rows) == len(table_rows) - 1

    core.db.remove_table(table_name)

    assert not core.db.table_exists(table_name)



