# coding: utf-8
import pytest


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
