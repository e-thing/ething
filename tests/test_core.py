# coding: utf-8
import pytest


def test_core(core):

    content = b'hello world'

    def create_file():
        f = core.create('File', {
            'name': 'file1.txt'
        })

        f.write(content)

    count = 2
    for _ in range(0, count):
        create_file()

    assert len(core.find()) == count

    usage = core.usage()

    print(usage)

    assert usage.get('used') == len(content) * count
