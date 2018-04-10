# coding: utf-8

import pytest

from ething.Resource import Resource
from ething.base import attr, isInteger


def test_resource(core):
    
    @attr('val', validator = isInteger(), default = 12)
    class A(Resource):
        pass
    
    class B(Resource):
        pass
    
    class C(B):
        pass
    
    
    a = core.create('A', {
        'name' : 'r_a'
    })
    
    assert a.val == 12
    
    b = core.create('B', {
        'name' : 'r_b',
        'createdBy': a
    })
    
    c = core.create('C', {
        'name' : 'r_c',
        'createdBy': b
    })
    
    assert len(core.find()) == 3
    
    assert c.isTypeof('B')
    
    a.remove(removeChildren=True)
    
    assert len(core.find()) == 0
    
    
    
    