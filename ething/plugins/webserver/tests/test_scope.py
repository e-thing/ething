# coding: utf-8
import pytest
from ..Scope import validate


def test_scope_validate():

    assert validate('settings:read  resource:read ')  # True
    assert not validate('file:write  ddd:invalide ')  # False
