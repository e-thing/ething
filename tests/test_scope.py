# coding: utf-8
import pytest
from ething.Scope import Scope

def test_scope_validate():
    
    assert Scope.validate('settings:read  app:read ') # True
    assert not Scope.validate('file:write  ddd:invalide ') # False
    


