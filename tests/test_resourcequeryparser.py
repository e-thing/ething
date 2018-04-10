# coding: utf-8
import pytest
from ething.ResourceQueryParser import ResourceQueryParser


@pytest.mark.parametrize("expr,valid", [
    ("name == 'toto'", True),
    ("hasIcon == true", True),
    ("  ", False),
])
def test_resourcequeryparser(expr, valid):
    ok, message = ResourceQueryParser.check(expr)
    assert ok is valid
    
    