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

    # reduce the verbosity
    LOGGER.setLevel(logging.INFO)


if zigate_lib_imported:

    from ething.TransportProcess import SerialTransport, NetTransport
    from ething.reg import *
    from ething.plugin import Plugin
    from ething.env import USER_DIR
    from ething import scheduler
    from ething.core import PairingUpdated
    import os
    import time
    import json
    from zigate import dispatcher, core as zigate_core
    from zigate.core import DeviceEncoder
    from zigate.transport import BaseTransport
    from . import devices
    from .devices import zigate_device_classes

    PERSISTENT_FILE = os.path.abspath(os.path.join(USER_DIR, 'zigate.json'))

    CONNECTED = 'CONNECTED'
    DISCONNECTED = 'DISCONNECTED'

    DISCOVERY_TIMEOUT = 15  # the amount of seconds to wait for the discovey to be completed
    DISCOVERY_TIMEOUT_EXTRA = 5  # the amount of seconds to wait if the discovey mode is auto-discovered

    zigate_core.LOGGER = logging.getLogger(__name__)

    @meta(description='''
    ![ZiGate Logo](https://i2.wp.com/zigate.fr/wp-content/uploads/2017/10/cropped-ZiGate_black2-1.png?fit=198%2C100&ssl=1)
    See for more details : https://zigate.fr
    ''', icon='mdi-alpha-z-box')
    @attr('ieee', type=String(), default='', mode=READ_ONLY, description="The ieee address of the gateway")
    @attr('addr', type=String(), default='', mode=READ_ONLY, description="The network address of the gateway")
    @attr('version', type=String(), default='', mode=READ_ONLY, description="The version of the gateway")
    @attr('channel', type=Integer(), default=0, mode=READ_ONLY, description="The channel used by the zigbee network")
    @attr('connected', type=Boolean(), default=False, mode=READ_ONLY, description="Set to true when connected to the zigate gateway.")
    class ZigatePlugin(Plugin):

        def setup(self):
            self.black_listed_devices = list()
            self.z = None

            if not os.path.exists(PERSISTENT_FILE):
                with open(PERSISTENT_FILE, 'w') as fp:
                    fp.write("{}")

            self.core.bind(PairingUpdated, self._on_pairing_updated)

        def _on_pairing_updated(self, signal):
            pairing = signal.data['state']
            if pairing:
                self.start_pairing_mode()
            else:
                self.stop_pairing_mode()

        def _connect(self, **kwargs):
            wifi_version = self.options.get('wifi_version', 'no').lower()
            if wifi_version in ('1', 'y', 'yes', 'true'):
                if not self.options.get('host'):
                    self.logger.warning("no host set in the configuration file")
                    self.notification.warning('no host set in the configuration file', title='Zigate', id='zigate.check')
                    self.connected = False
                    return
                else:
                    self.notification.remove('zigate.check')
                    return ZigateWifi(self, **kwargs)
            else:
                if not self.options.get('serial_port'):
                    self.logger.warning("no serial_port set in the configuration file")
                    self.notification.warning('no serial_port set in the configuration file', title='Zigate', id='zigate.check')
                    self.connected = False
                    return
                else:
                    self.notification.remove('zigate.check')
                    return ZigateSerial(self, **kwargs)

        @scheduler.set_interval(30, name="zigate.save_state")
        def save_state(self):
            if hasattr(self, 'z') and self.z:
                _activity = getattr(self, '_activity', 0)
                if _activity != getattr(self, '_activity_last', 0):
                    self.z.save_state()
                    self._activity_last = _activity

        @scheduler.delay(0, name="zigate.init")
        def _controller_start(self):
            self._controller_end()  # just in case of restart

            self.logger.debug('zigate controller start')

            gconf = {'auto_start': False, 'auto_save': False, 'path': PERSISTENT_FILE}

            self.z = z = self._connect(**gconf)
            if z is None:
                return

            self._activity = 0

            dispatcher.connect(self._controller_callback, signal=zigate.ZIGATE_DEVICE_ADDED, sender=z)
            dispatcher.connect(self._controller_callback, signal=zigate.ZIGATE_DEVICE_UPDATED, sender=z)
            dispatcher.connect(self._controller_callback, signal=zigate.ZIGATE_DEVICE_REMOVED, sender=z)
            dispatcher.connect(self._controller_callback, signal=zigate.ZIGATE_DEVICE_ADDRESS_CHANGED, sender=z)
            dispatcher.connect(self._controller_callback, signal=zigate.ZIGATE_ATTRIBUTE_ADDED, sender=z)
            dispatcher.connect(self._controller_callback, signal=zigate.ZIGATE_ATTRIBUTE_UPDATED, sender=z)
            dispatcher.connect(self._controller_callback, signal=zigate.ZIGATE_DEVICE_NEED_DISCOVERY, sender=z)
            dispatcher.connect(self._controller_callback, signal=CONNECTED, sender=z)
            dispatcher.connect(self._controller_callback, signal=DISCONNECTED, sender=z)

            # start transport
            self.z.setup_connection()

        def _controller_init(self):
            self.logger.debug('zigate startup')

            devices = self.core.find(lambda r: r.typeof('resources/ZigateBaseDevice'))
            # reset some attributes
            for d in devices:
                if d.error:
                    d.error = None

            first_start = not self.ieee and not self.addr and not devices

            if first_start:
                # reset everything
                self.logger.warning('first start, reset zigate key: erase all persistant data')
                self.z.erase_persistent()

            self.z.startup()

            version = self.z.get_version_text(refresh=True)

            self.logger.info('zigate version: %s', version)

            with self:
                self.version = version
                self.addr = self.z.addr
                self.ieee = self.z.ieee
                self.channel = self.z.channel

            self.z.get_devices_list(wait=True)
            self.z.cleanup_devices()

            # refresh devices
            devices = self.core.find(lambda r: r.typeof('resources/ZigateBaseDevice')) # need to refresh the list
            for d in devices:
                zdevice = d.zdevice
                if zdevice:
                    self.logger.debug('refreshing device %s', d)
                    zdevice.refresh_device()
                else:
                    d.error = 'the device is no longer paired'
                    self.logger.warning('the device %s is no longer paired', d)

            for zinstance in self.z.devices:
                for d in devices:
                    if d.ieee == zinstance.ieee:
                        break
                else:
                    # not found: try to create it !
                    self._create_devices(zinstance, force=True, notify=False)

        def _controller_end(self):
            if hasattr(self, 'z') and self.z:
                self.logger.debug('zigate controller stop')
                dispatcher.disconnect(self._controller_callback, signal=zigate.ZIGATE_DEVICE_ADDED, sender=self.z)
                dispatcher.disconnect(self._controller_callback, signal=zigate.ZIGATE_DEVICE_UPDATED, sender=self.z)
                dispatcher.disconnect(self._controller_callback, signal=zigate.ZIGATE_DEVICE_REMOVED, sender=self.z)
                dispatcher.disconnect(self._controller_callback, signal=zigate.ZIGATE_DEVICE_ADDRESS_CHANGED, sender=self.z)
                dispatcher.disconnect(self._controller_callback, signal=zigate.ZIGATE_ATTRIBUTE_ADDED, sender=self.z)
                dispatcher.disconnect(self._controller_callback, signal=zigate.ZIGATE_ATTRIBUTE_UPDATED, sender=self.z)
                dispatcher.disconnect(self._controller_callback, signal=zigate.ZIGATE_DEVICE_NEED_DISCOVERY, sender=self.z)
                dispatcher.disconnect(self._controller_callback, signal=CONNECTED, sender=self.z)
                dispatcher.disconnect(self._controller_callback, signal=DISCONNECTED, sender=self.z)
                self.z.save_state()
                self.z.close()
                self.z = None

        def _controller_callback(self, sender, signal, **kwargs):

            self.logger.debug('signal received: %s %s', signal, kwargs)

            if signal == DISCONNECTED:
                self.connected = False
                return

            self.connected = True

            if signal == CONNECTED:
                # run in a new process because it is blocking
                self.processes.add(self._controller_init, id="zigate.setup")
                return

            if 'device' in kwargs:
                dz_instance = kwargs.get('device')
                ieee = dz_instance.ieee
                if not ieee:
                    return

                devices = self.core.find(lambda r: r.typeof('resources/ZigateBaseDevice') and r.ieee == ieee)

                if not devices:
                    if signal == zigate.ZIGATE_DEVICE_ADDED or signal == zigate.ZIGATE_DEVICE_UPDATED or signal == zigate.ZIGATE_DEVICE_ADDRESS_CHANGED:
                        # new devices
                        devices = self._create_devices(dz_instance) or []

                for device in devices:
                    with device:
                        device.process_signal(signal, kwargs)

            self._activity += 1

        def _wait_device_discovery(self, dz_instance):
            self.logger.debug('wait for the device %s to complete the discovery process', dz_instance)
            setattr(dz_instance, 'wait_discovery', True)
            t0 = time.time()

            while not dz_instance.discovery and time.time() - t0 < DISCOVERY_TIMEOUT:
                time.sleep(0.5)

            if dz_instance.discovery:

                if dz_instance.discovery == 'auto-discovered':
                    # wait a little longer for the attribute_discovery_request to complete
                    t0 = time.time()
                    while not dz_instance.discovery and time.time() - t0 < 5:
                        time.sleep(0.5)

                self.logger.debug('discovery process done for the device %s , discovery mode=%s', dz_instance,
                                  dz_instance.discovery)

            else:
                self.logger.warning('unable to complete the discovery of the device %s', dz_instance)

            delattr(dz_instance, 'wait_discovery')

            self._create_devices(dz_instance, force=True)

        def _create_devices(self, dz_instance, force=False, notify=True):

            ieee = dz_instance.ieee

            if not ieee:
                return

            if ieee in self.black_listed_devices:
                return

            if getattr(dz_instance, 'wait_discovery', False) is True:
                return

            dev_type = dz_instance.get_value('type')
            dev_name = dev_type or ('address: 0x%s' % dz_instance.addr)
            notif_id = 'zigate.create.%s' % dz_instance.addr

            if not force and not dz_instance.discovery:
                # wait for the discovery process to complete
                process_id = '%s.wait_discovery' % ieee
                if process_id not in self.processes:
                    self.logger.info('new device detected : %s', dz_instance)
                    if notify:
                        self.notification.info('Pairing device: %s. Please wait...' % dev_name,
                                               timeout=DISCOVERY_TIMEOUT + DISCOVERY_TIMEOUT_EXTRA, id=notif_id)
                    self.processes.add(self._wait_device_discovery, id=process_id, args=(dz_instance,))
                return

            # print some info here
            info = dz_instance.to_json(properties=True)
            info['actions'] = dz_instance.available_actions()
            self.logger.info(json.dumps(info, indent=4, sort_keys=True, cls=DeviceEncoder))

            if dev_type is None:
                self.logger.warning('no type found for device for %s , try to pair it again', dz_instance)
                if notify:
                    self.notification.warning('incomplete discovery, try to pair it again', timeout=10, id=notif_id)
            else:
                devices = []

                for cls in zigate_device_classes:
                    if hasattr(cls, 'isvalid'):
                        try:
                            r = cls.isvalid(self,
                                            dz_instance)  # returns either True/False or a class or a list of class
                            if r:
                                if r is True:
                                    r = cls
                                if not isinstance(r, list):
                                    r = [r]
                                for c in r:
                                    try:
                                        d = c.create_device(self, dz_instance)
                                        devices.append(d)
                                    except:
                                        self.logger.exception('zigate cls create exception for class %s', c)
                                return devices
                        except:
                            self.logger.exception('zigate cls isvalid exception for class %s', cls)

                # search by endpoints
                for ep in dz_instance.endpoints:
                    for cls in zigate_device_classes:
                        if hasattr(cls, 'isvalid_ep'):
                            try:
                                r = cls.isvalid_ep(self, dz_instance, ep)  # returns either True/False or a class
                                if r:
                                    if r is True:
                                        r = cls
                                    try:
                                        d = r.create_device(self, dz_instance, ep)
                                        devices.append(d)
                                        break
                                    except:
                                        self.logger.exception('zigate cls create exception for class %s', r)
                            except:
                                self.logger.exception('zigate cls isvalid_ep exception for class %s', cls)

                if devices:
                    self.notification.remove(notif_id)
                    return devices

                # self.black_listed_devices.append(ieee)
                if notify:
                    self.notification.warning('unknown device: %s' % dev_name, timeout=10, id=notif_id)

            self.logger.warning('unable to create any device for %s', dz_instance)

        def start_pairing_mode(self, duration=60):
            """
            start pairing mode for 60 seconds
            """
            if self.z:
                self.z.permit_join(duration)

        def stop_pairing_mode(self):
            """
            stop pairing mode
            """
            if self.z:
                self.z.stop_permit_join()


    class WrapperConnection(BaseTransport):

        def __init__(self, zigate_instance, transport):
            BaseTransport.__init__(self)
            self._running = False
            self.zigate_instance = zigate_instance
            self.plugin = zigate_instance.plugin
            self.core = zigate_instance.plugin.core
            self.transport = transport
            self._is_open = False
            self.reconnect_delay = 15

            self.plugin.processes.add(id="zigate.transport", target=self.main, terminate=self._stop)

        def is_connected(self):
            return self._is_open

        def _stop(self):
            self._running = False

        def main(self):
            self._running = True

            while self._running:

                error = None

                try:
                    self.transport.open()
                except Exception as e:
                    LOGGER.exception('exception in transport.open()')
                    error = e

                while not error and self._running and self.transport.is_open:

                    if not self._is_open:
                        self._is_open = True
                        dispatcher.send(CONNECTED, self.zigate_instance)

                    try:
                        # read all that is there or wait for one byte (blocking)
                        data = self.transport.read()
                    except Exception as e:
                        # probably some I/O problem such as disconnected USB serial
                        # adapters -> exit
                        LOGGER.exception('exception in transport')
                        error = e
                    else:
                        if data:
                            # make a separated try-except for called used code
                            try:
                                self.read_data(data)
                            except Exception as e:
                                LOGGER.exception('exception in protocol.data_received()')
                                error = e

                self._is_open = False
                dispatcher.send(DISCONNECTED, self.zigate_instance)

                if self.transport.is_open:
                    try:
                        self.transport.close()
                    except Exception as e:
                        LOGGER.exception('exception in transport.close()')

                t_end = time.time() + self.reconnect_delay
                while self._running and time.time() < t_end:
                    time.sleep(1.)
                LOGGER.debug('reconnecting...')

        def send(self, data):
            self.transport.write(data)

        def close(self):
            del self.plugin.processes['zigate.transport']


    class ZigateSerial(zigate.ZiGate):
        def __init__(self, plugin, **kwargs):
            port = plugin.options.get('serial_port')
            super(ZigateSerial, self).__init__(port, **kwargs)
            self.plugin = plugin

        def setup_connection(self):
            if self.connection is None:
                self.connection = WrapperConnection(self, transport=SerialTransport(self._port, 115200))


    class ZigateWifi(zigate.ZiGateWiFi):
        def __init__(self, plugin, **kwargs):
            host = plugin.options.get('host')
            port = int(plugin.options.get('wifi_port', 9999))
            super(ZigateWifi, self).__init__(host, port, **kwargs)
            self.plugin = plugin

        def setup_connection(self):
            if self.connection is None:
                self.connection = WrapperConnection(self, transport=NetTransport(self._host, self._port))
