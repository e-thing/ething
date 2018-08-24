# coding: utf-8
import pytest


def test_dbfs(core):

    content = b'hello world'

    id = core.db.storeFile('fff.txt', content, {
        'attr': 'attrvalue'
    })

    result = core.db.retrieveFile(id)

    assert len(core.db.listFiles()) == 1

    assert core.db.getFileSize(id) == len(content)

    assert core.db.retrieveFile(id) == content

    assert core.db.getFileMetadata(id).get('attr') == 'attrvalue'

    core.db.removeFile(id)

    assert core.db.listFiles() == []
