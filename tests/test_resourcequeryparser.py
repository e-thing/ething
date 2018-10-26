# coding: utf-8
import pytest
from ething.core.ResourceQueryParser import ResourceQueryParser


@pytest.mark.parametrize("expr,valid", [
    ("name == 'toto'", True),
    ("name=='toto'", True),
    ('name=="toto"', True),
    ("id == 'abcdefg'", True),
    ("size > 0", True),
    ("  ", False),
])
def test_resourcequeryparser_valid(core, expr, valid):
    ok, message = core.resourceQueryParser.check(expr)

    print(message)

    assert ok is valid


def test_resourcequeryparser(core):

    core.create('resources/File', {
        'name': 'file1.txt',
        'expireAfter': 300
    })

    core.create('resources/File', {
        'name': 'file2.txt',
        'data': {
            'foo': 'bar'
        }
    })

    core.create('resources/Table', {
        'name': 'table1'
    })

    assert len(core.find('type == "resources/File"')) == 2
    assert len(core.find('data.foo == "bar"')) == 1
    assert len(core.find('data has "foo"')) == 1
    assert len(core.find('data.foo exists')) == 1
    assert len(core.find('name == "file1.txt" and data is "object"')) == 1
    assert len(core.find('extends has "resources/File"')) == 2
    assert len(core.find('expireAfter == null')) == 2
    assert len(core.find('expireAfter is "null"')) == 2
    assert len(core.find('expireAfter is "number"')) == 1
    assert len(core.find('expireAfter > 100')) == 1
