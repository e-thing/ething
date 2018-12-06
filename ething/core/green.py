# coding: utf-8
from functools import wraps


mode = 'threading'

try:
    from gevent import monkey, events, config

except ImportError:

    try:
        import eventlet
    except ImportError:

        def _non_blocking_run(method, args, kwargs):
            return method(*args, **kwargs)

    else:
        mode = 'eventlet'

        eventlet.monkey_patch(select=False)  # every use of select (blocking) must be done in a ThreadProcess
        # from eventlet.debug import hub_blocking_detection, spew
        # hub_blocking_detection(state=True, resolution=1)

        from eventlet import tpool

        def _non_blocking_run(method, args, kwargs):
            return tpool.execute(method, *args, **kwargs)

else:
    mode = 'gevent'
    monkey.patch_all()

    config.max_blocking_time = 1.0
    config.monitor_thread = True

    def event_handler(event):
        if isinstance(event, events.EventLoopBlocked):
            print('DBG: %s' % event)
            #print(event.greenlet)
            #print('****')
            #print(event.info)
            #print(event.blocking_time)

    events.subscribers.append(event_handler)

    from gevent.hub import get_hub

    def _non_blocking_run(method, args, kwargs):
        return get_hub().threadpool.apply(method, args, kwargs)


def make_it_green(method):
    @wraps(method, ['__name__', '__doc__'])
    def apply(*args, **kwargs):
        return _non_blocking_run(method, args, kwargs)
    return apply

print('initialized for %s' % mode)
