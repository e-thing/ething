# coding: utf-8
import pytest
from ething.base import DataObject, attr, isString, isNumber


def test_base():
    
    db = {}
    
    @attr('name', validator = isString(allow_empty = False))
    @attr('val', validator = isNumber(), default = 45)
    class A(DataObject):
        
        def _insert(self, data):
            db[self.name] = data
        
        def _save(self, data):
            db[self.name] = data
        
        def _refresh(self):
            return db[self.name]
        
    
    a = A()
    a.name = 'toto'
    a.save()
    
    assert a.name == 'toto'
    assert db['toto'].get('name') == 'toto'
    
    assert a.val == 45
    
    with a:
        a.val = 62
    
    assert db['toto'].get('val') == 62
    
    
    @attr('val', default = 12)
    class B(A):
        pass
    
    
    b = B()
    assert b.val == 12
    
    with pytest.raises(AttributeError):
        b.val = 'invalid' # must be a number
    
    with pytest.raises(AttributeError):
        b.save() # name is not set
    