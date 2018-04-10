# coding: utf-8
import pytest
from bson.objectid import ObjectId


def test_dbfs(core):
    
    content = b'hello world'
    
    id = core.fs.storeFile('fff.txt', content, {
        'attr' : 'attrvalue'
    })
    
    result = core.fs.retrieveFile(id)
    
    assert isinstance(id, ObjectId)
    
    assert len(core.fs.listFiles()) == 1
    
    assert core.fs.getFileSize(id) == len(content)
    
    assert core.fs.retrieveFile(id) == content
    
    assert core.fs.getFileMetadata(id).get('attr') == 'attrvalue'
    
    core.fs.removeFile(id)
    
    assert core.fs.listFiles() == []
    
    

