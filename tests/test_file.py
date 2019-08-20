# coding: utf-8
import pytest
from ething.core.File import File
import requests


def test_file_create(core):
    content = b'hello world'

    f = core.create('resources/File', {
        'name': 'file1.txt'
    })

    assert isinstance(f, File)

    f.write(content)

    f = core.get(f.id)

    assert isinstance(f, File)

    assert f.read() == content

    assert f.size == len(content)


def test_file_delete(core):
    content = b'hello world'

    f = core.create('resources/File', {
        'name': 'file1.txt'
    })

    assert isinstance(f, File)

    f.remove()

    with pytest.raises(KeyError):
        f = core.get(f.id)

def test_file_image(core):

    r = requests.get(
        'https://www.w3schools.com/w3css/img_fjords.jpg', stream=True)
    if r.status_code == 200:

        f = core.create('resources/File', {
            'name': 'image.jpg'
        })

        assert isinstance(f, File)

        f.write(r.content)

        f = core.get(f.id)

        assert f.mime == 'image/jpeg'


def test_file_encoding(core):
    content = u'bonjour rémi'

    f = core.create('resources/File', {
        'name': 'file1.txt'
    })

    assert isinstance(f, File)

    f.write(content, encoding='utf8')

    f = core.get(f.id)

    assert isinstance(f, File)

    assert f.read(encoding='utf8') == content

    assert f.size == len(content.encode('utf8'))


def test_file_append(core):
    content1 = b'hello'
    content2 = b' world'

    f = core.create('resources/File', {
        'name': 'file1.txt'
    })

    assert isinstance(f, File)

    f.write(content1)
    f.write(content2, append=True)

    assert f.read() == (content1+content2)
