# coding: utf-8
import pytest
from ..Scope import Scope


def test_scope_validate():

    assert Scope.validate('settings:read  resource:read ')  # True
    assert not Scope.validate('file:write  ddd:invalide ')  # False
