
from gevent import monkey, getcurrent, time

monkey.patch_all()

# if you want logging
import logging
logging.basicConfig()
logging.root.setLevel(logging.DEBUG)


import zigate
from zigate import dispatcher
from zigate.core import FakeZiGate, DeviceEncoder

import time
import json


def print_devices(z):
    for device in z.devices:
        print('----- device -----')
        print(str(device))
        print('device addr: %s' % str(device.addr))
        print('device genericType: %s' % str(device.genericType))
        print('device info: %s' % str(device.info))
        print('device endpoints: %s' % str(device.endpoints))
        print('device discovery: %s' % str(device.discovery))
        for prop in device.properties:
            print(prop)
        print('------------------')


def z_callback(sender, signal, **kwargs):
    print('----- signal dispatcher -----')
    print('sender: %s' % sender)  # zigate instance
    print('signal: %s' % signal)  # one of EVENT
    print('kwargs:')
    for d in kwargs:
        print('  +  %s: %s' % (d, kwargs[d]))  # contains device and/or attribute changes, etc
    if 'device' in kwargs:
        print('')
        device = kwargs.get('device')
        print('device: %s' % device)
        print(json.dumps(device.to_json(properties=True), indent=4, sort_keys=True, cls=DeviceEncoder))
    print('-----------------------------')


# dispatcher.connect(z_callback, dispatcher.Any)
dispatcher.connect(z_callback, zigate.ZIGATE_DEVICE_ADDED)
dispatcher.connect(z_callback, zigate.ZIGATE_DEVICE_UPDATED)
dispatcher.connect(z_callback, zigate.ZIGATE_DEVICE_REMOVED)
dispatcher.connect(z_callback, zigate.ZIGATE_DEVICE_ADDRESS_CHANGED)
dispatcher.connect(z_callback, zigate.ZIGATE_ATTRIBUTE_ADDED)
dispatcher.connect(z_callback, zigate.ZIGATE_ATTRIBUTE_UPDATED)
dispatcher.connect(z_callback, zigate.ZIGATE_DEVICE_NEED_DISCOVERY)



channel = 0
port = None # if None, first device will be selected

z = FakeZiGate(auto_start=False, auto_save=False, path=None)
#z = zigate.connect(port=port, auto_start=False, auto_save=False, path=None) # Leave None to auto-discover the port

z.startup(channel)


print('version: %s' % z.get_version_text())


# refresh devices list (already done in startup)
# z.get_devices_list()

print_devices(z)

# start inclusion mode
#z.permit_join()
#z.is_permitting_join()




while True:
    time.sleep(1.)


z.close()