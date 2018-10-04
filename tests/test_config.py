# coding: utf-8
import pytest


def test_config(core):

    config = core.config

    assert config.get('my.conf.not.present', 45) == 45

    config.set('my.conf.foo', 'bar')

    assert config.get('my.conf.foo') == 'bar'
