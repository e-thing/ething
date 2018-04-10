# coding: utf-8
import pytest



def test_config(core):
    
    config = core.config
    
    assert config.get('my.conf.not.present', 45) == 45
    
    config('my.conf.foo', 'bar')
    
    assert config('my.conf.foo') == 'bar'
    
    