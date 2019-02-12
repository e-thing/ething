# coding: utf-8
import pytest
from ething.core.utils import ShortId



def test_shortid_duplicate():

    ids = []
    for i in range(0, 100000):
        ids.append(ShortId.generate())

    import collections

    assert len([item for item, count in collections.Counter(
        ids).items() if count > 1]) == 0
