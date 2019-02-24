# coding: utf-8
from functools import wraps
from gevent import monkey, getcurrent, time

monkey.patch_all()

from gevent.hub import get_hub


def get_current():
    return getcurrent()


def event_loop():
    time.sleep(0) # do the switching stuff


def make_it_green(method):
    @wraps(method, ['__name__', '__doc__'])
    def apply(*args, **kwargs):
        return get_hub().threadpool.apply(method, args, kwargs)
    return apply

