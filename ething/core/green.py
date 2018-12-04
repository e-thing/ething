# coding: utf-8


mode = 'threading'

try:
    from gevent import monkey

except ImportError:

    try:
        import eventlet
    except ImportError:
        pass
    else:
        mode = 'eventlet'

        eventlet.monkey_patch(select=False)  # every use of select (blocking) must be done in a ThreadProcess
        # from eventlet.debug import hub_blocking_detection, spew
        # hub_blocking_detection(state=True, resolution=1)

else:
    mode = 'gevent'
    monkey.patch_all()


print('initialized for %s' % mode)
