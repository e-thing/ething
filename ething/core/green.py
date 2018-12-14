# coding: utf-8
from functools import wraps


mode = 'threading'

try:
    from gevent import monkey, getcurrent, time

except ImportError:

    try:
        import eventlet
    except ImportError:

        import threading

        def _non_blocking_run(method, args, kwargs):
            return method(*args, **kwargs)

        def get_current():
            return threading.current_thread()

        def event_loop():
            pass

    else:
        mode = 'eventlet'

        eventlet.monkey_patch(select=False)  # every use of select (blocking) must be done in a ThreadProcess
        # from eventlet.debug import hub_blocking_detection, spew
        # hub_blocking_detection(state=True, resolution=1)

        from eventlet import tpool

        def _non_blocking_run(method, args, kwargs):
            return tpool.execute(method, *args, **kwargs)

        def get_current():
            return eventlet.getcurrent()

        def event_loop():
            eventlet.sleep(0)

else:
    mode = 'gevent'
    monkey.patch_all()

    from gevent.hub import get_hub

    def _non_blocking_run(method, args, kwargs):
        return get_hub().threadpool.apply(method, args, kwargs)

    def get_current():
        return getcurrent()

    def event_loop():
        time.sleep(0) # do the switching stuff


if mode == 'threading':
    def make_it_green(method):
        return method
else:
    def make_it_green(method):
        @wraps(method, ['__name__', '__doc__'])
        def apply(*args, **kwargs):
            return _non_blocking_run(method, args, kwargs)
        return apply


print('initialized for %s' % mode)
