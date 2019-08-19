# coding: utf-8

try:
    import zigate
except Exception as e:
    zigate_lib_imported = False
    print("WARNING: unable to import the package 'zigate' (https://github.com/doudz/zigate): %s" % str(e))
else:
    zigate_lib_imported = True

    from zigate.core import LOGGER
    import logging

    LOGGER.setLevel(logging.DEBUG)


if zigate_lib_imported:
    from . import gateways
    from . import devices
