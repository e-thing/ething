# coding: utf-8
import pytest
from ething.ShortId import ShortId


@pytest.mark.parametrize("id,valid", [
    ("1234567", True),
    ("123456", False),
    ("123?f56", False),
])
def test_shortid(id, valid):
    assert ShortId.validate(id) is valid


@pytest.mark.skip()
def test_shortid_duplicate():

    ids = []
    for i in range(0, 1000):
        ids.append(ShortId.generate())

    import collections

    assert len([item for item, count in collections.Counter(
        ids).items() if count > 1]) == 0
