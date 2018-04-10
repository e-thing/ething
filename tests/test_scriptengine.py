# coding: utf-8
import pytest
from ething.ScriptEngine import ScriptEngine


@pytest.mark.nodejs
def test_scriptengine(core):
    
    result = ScriptEngine.run(core, 'console.log("toto")');
    
    assert result.get('ok') is True
    
    