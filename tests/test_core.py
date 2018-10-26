# coding: utf-8
import pytest
from ething.core.utils.export import export_data, import_data
from ething.core import Core


def test_core(core):

    content = b'hello world'

    before_count = len(core.find())

    def create_file():
        f = core.create('resources/File', {
            'name': 'file1.txt'
        })

        f.write(content)

    count = 2
    for _ in range(0, count):
        create_file()

    assert len(core.find()) == before_count + count

    usage = core.usage()

    print(usage)

    assert usage.get('used') >= 0


def test_import_export(core):

    core.config.set('foo', 'bar')

    file_content = b'hello world'
    f = core.create('resources/File', {
        'name': 'file1.txt'
    })
    f.write(file_content)

    table_content = [{
        "a": 1,
        "b": False,
        "c": 4.5,
        "d": "string"
    }, {
        "a": 2
    }, {
        "a": 3
    }]
    t = core.create('resources/Table', {
        'name': 'table0'
    })
    t.importData(table_content)


    exported_data = export_data(core)

    core2 = Core()
    core2.init()

    import_data(core2, exported_data)

    assert core2.config.get('foo') == 'bar'

    assert core2.get(f.id)

    assert core2.get(f.id).read() == file_content

    assert core2.get(t.id)

    assert len(core2.get(t.id).select()) == len(table_content)
