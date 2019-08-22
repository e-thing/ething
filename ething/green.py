# coding: utf-8
from functools import wraps
from gevent import monkey, getcurrent, time
import logging


__all__ = [
    'event_loop',
    'make_it_green',
    'install_debugger',
    'get_current'
]


LOGGER = logging.getLogger(__name__)

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


_gevent_dbg_installed = False


def install_debugger():
    global _gevent_dbg_installed

    if _gevent_dbg_installed:
        return

    from gevent import events, config

    LOGGER.warning('install gevent debugger')

    _gevent_dbg_installed = True

    config.max_blocking_time = 1.0
    config.monitor_thread = True

    def event_handler(event):
        if isinstance(event, events.EventLoopBlocked):
            LOGGER.warning('DBG: %s', event)

    events.subscribers.append(event_handler)
