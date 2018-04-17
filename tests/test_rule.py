# coding: utf-8
import pytest
from ething.meta import get_signal_class, get_event_class


def test_rule(core):
    
    script_content = u'console.log("toto")'
    
    script = core.create('File', {
        'name' : 'script.js'
    })
    
    script.write(script_content, encoding = 'utf8')
    
    
    rule = core.create('Rule', {
        'name' : 'myrule',
        'script': script,
        'event': {
            'type': 'CustomEvent',
            'name': 'test'
        }
    })
    
    
    assert rule
    
    signal = get_signal_class('Custom')('test')
    
    assert rule.run(signal)
    
    assert rule.script_return_code == 0
    assert rule.script_execution_count == 1
    