# coding: utf-8
import pytest
from ething.core.type import *
import pytz


def test_dict():

    t = Dict(mapping={
        'foo': String(),
        'bar': Number(min=0)
    })

    t.set({
        'foo': 'toto',
        'bar': 5
    })

    with pytest.raises(ValueError):
        t.set({
            'foo': 'toto',
            'bar': -5
        })

    with pytest.raises(ValueError):
        t.set({
            'foo': 'toto'
        })


def test_date():

    hki = pytz.timezone('Europe/Helsinki')

    t1 = Date(ignore_tz=False, tz=pytz.utc, to_utc=pytz.utc)
    t2 = Date(ignore_tz=False, from_tz=hki, tz=pytz.utc, to_utc=pytz.utc)

    d_naive = datetime.datetime(2012, 10, 29, 10, 34, 0)
    d_aware_utc = pytz.utc.localize(d_naive)
    d_aware_hki = d_aware_utc.astimezone(hki)

    with pytest.raises(ValueError):
        d = t1.set(d_naive)

    d = t2.set(d_aware_hki.replace(tzinfo=None)) # make it naive

    assert d == d_aware_utc

    d = t2.set(d_aware_hki)  # make it naive

    assert d == d_aware_utc



