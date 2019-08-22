# coding: utf-8
import pytest
from ething.utils import generate_id



def test_shortid_duplicate():

    ids = []
    for i in range(0, 100000):
        ids.append(generate_id())

    import collections

    assert len([item for item, count in collections.Counter(
        ids).items() if count > 1]) == 0
