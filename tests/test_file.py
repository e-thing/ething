# coding: utf-8
import pytest
from ething.File import File
import requests


def test_file_create(core):
    content = b'hello world'

    f = core.create('File', {
        'name': 'file1.txt'
    })

    assert isinstance(f, File)

    f.write(content)

    f = core.get(f.id)

    assert isinstance(f, File)

    assert f.read() == content

    assert f.size == len(content)


def test_file_image(core):

    r = requests.get(
        'https://www.w3schools.com/w3css/img_fjords.jpg', stream=True)
    if r.status_code == 200:

        f = core.create('File', {
            'name': 'image.jpg'
        })

        assert isinstance(f, File)

        f.write(r.content)

        f = core.get(f.id)

        assert f.mime == 'image/jpeg'

        assert f.readThumbnail() is not None


def test_file_encoding(core):
    content = u'bonjour rémi'

    f = core.create('File', {
        'name': 'file1.txt'
    })

    assert isinstance(f, File)

    f.write(content, encoding='utf8')

    f = core.get(f.id)

    assert isinstance(f, File)

    assert f.read(encoding='utf8') == content

    assert f.size == len(content.encode('utf8'))
