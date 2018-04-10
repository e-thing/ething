# coding: utf-8
import pytest
from ething.App import App

def test_app_create(core):
    content = u'<div>Bonjour rémi</div>'
    
    f = core.create('App', {
        'name' : 'myapp'
    })
    
    f.setScript(content, encoding = 'utf8')
    
    assert isinstance(f, App)
    
    f = core.get(f.id)
    
    assert isinstance(f, App)
    
    assert f.readScript(encoding = 'utf8') == content


