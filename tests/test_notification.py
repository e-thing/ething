# coding: utf-8
import pytest
import time


def test_notification_remove(core):
    nb0 = len(core.notification.find())

    nid = core.notification.info('message', id='foo')

    assert nid == 'foo'
    assert len(core.notification.find()) == nb0 + 1

    core.notification.remove(nid)

    assert len(core.notification.find()) == nb0


def test_notification_timeout(core):
    nb0 = len(core.notification.find())

    core.notification.info('message', id='foo', timeout=1)

    assert len(core.notification.find()) == nb0 + 1

    time.sleep(1.5)

    assert len(core.notification.find()) == nb0


