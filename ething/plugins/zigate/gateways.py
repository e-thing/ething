# coding: utf-8
import zigate
from zigate import dispatcher
from zigate.core import DeviceEncoder
from zigate.transport import BaseTransport
from future.utils import string_types
from ething.core.Device import Device
from ething.core.reg import *
from ething.core.Process import Process
from ething.core.env import USER_DIR
from ething.core import scheduler
from ething.core.TransportProcess import SerialTransport, NetTransport
from .devices import zigate_device_classes
import json
import os
import logging
import time


LOGGER = logging.getLogger("ething.zigate")


PERSISTENT_FILE = os.path.abspath(os.path.join(USER_DIR, 'zigate.json'))

black_listed_devices = list()


CONNECTED = 'CONNECTED'
DISCONNECTED = 'DISCONNECTED'


@abstract
@meta(description='''
![ZiGate Logo](https://i2.wp.com/zigate.fr/wp-content/uploads/2017/10/cropped-ZiGate_black2-1.png?fit=198%2C100&ssl=1)
See for more details : https://zigate.fr
''', icon='mdi-alpha-z-box')
@attr('ieee', type=String(), default='', mode = READ_ONLY, description="The ieee address of the gateway")
@attr('addr', type=String(), default='', mode = READ_ONLY, description="The network address of the gateway")
@attr('version', type=String(), default='', mode = READ_ONLY, description="The version of the gateway")
@attr('channel', type=Integer(), default=0, mode = READ_ONLY, description="The channel used by the zigbee network")
class ZigateBaseGateway(Device):

    RESET_ATTR = list(),

    def on_update(self, dirty_keys):
        for attr in self.RESET_ATTR:
            if attr in dirty_keys:
                self._controller_start()
                break

    @property
    def persistent_file(self):
        return os.path.abspath(os.path.join(USER_DIR, 'zigate_%s.json' % self.id))

    def _connect(self, **kwargs):
        raise NotImplementedError()

    @scheduler.setInterval(30, name="zigate.save_state")
    def save_state(self):
        if hasattr(self, 'z') and self.z:
            _activity = getattr(self, '_activity', 0)
            if _activity != getattr(self, '_activity_last', 0):
                self.log.debug('save_state')
                self.z.save_state()
                self._activity_last = _activity

    @scheduler.delay(0, name="zigate.init")
    def _controller_start(self):
        self._controller_end() # just in case...

        gconf = {'auto_start':False, 'auto_save':False, 'path':self.persistent_file}

        self.z = z = self._connect(**gconf)
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
        self.log.debug('zigate startup')

        # reset some attributes
        for d in self.children(lambda r: r.isTypeof(Device) and r.error):
            d.error = None

        self.z.startup()

        self.version = self.z.get_version_text(refresh=True)
        self.log.info('zigate version: %s', self.version)

        self.addr = self.z.addr
        self.ieee = self.z.ieee
        self.channel = self.z.channel

    def _controller_end(self):
        if hasattr(self, 'z') and self.z:
            self.log.info('zigate close')
            dispatcher.disconnect(self._controller_callback, sender=self.z)
            self.z.save_state()
            self.z.close()
            self.z = None

    def _controller_callback(self, sender, signal, **kwargs):

        self.log.debug('signal received: %s', signal)

        if signal == DISCONNECTED:
            self.refresh_connect_state(False)
            return

        self.refresh_connect_state(True)

        if signal == CONNECTED:
            # run in a new process because it is blocking
            self.core.process_manager.attach(Process(name="zigate.setup", target=self._controller_init))
            return

        if 'device' in kwargs:
            dz_instance = kwargs.get('device')

            if signal == zigate.ZIGATE_DEVICE_ADDED:
                # wait for the discovery process to complete
                self.core.scheduler.delay(5., callback=lambda: self.log.info(json.dumps(dz_instance.to_json(properties=True), indent=4, sort_keys=True, cls=DeviceEncoder)))

            devices = self.children(lambda r: r.ieee == dz_instance.ieee)
            if not devices:
                # new devices
                devices = self._create_devices(dz_instance)

            if devices:
                for device in devices:
                    with device:
                        device.process_signal(signal, kwargs)

        self._activity += 1

    def _create_devices(self, dz_instance):

        ieee = dz_instance.ieee

        if ieee in black_listed_devices:
            return

        self.log.info('new device: %s', dz_instance.info)
        devices = []

        for cls in zigate_device_classes:
            if hasattr(cls, 'isvalid'):
                try:
                    r = cls.isvalid(self, dz_instance) # returns either True/False or a class or a list of class
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
                                self.log.exception('zigate cls create exception for class %s', c)
                        return devices
                except:
                    self.log.exception('zigate cls isvalid exception for class %s', cls)

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
                                self.log.exception('zigate cls create exception for class %s', r)
                    except:
                        self.log.exception('zigate cls isvalid exception for class %s', cls)

        if devices:
            return devices

        black_listed_devices.append(ieee)
        self.log.warning('unable to create any device for %s', dz_instance)

    @method
    def start_pairing_mode(self):
        """
        start pairing mode for 60 seconds
        """
        if self.z:
            self.z.permit_join(60)

    @method
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
        self.gateway = zigate_instance.gateway
        self.core = zigate_instance.gateway.core
        self.transport = transport
        self.log = LOGGER
        self._is_open = False
        self.reconnect_delay = 15

        self._process = self.core.process_manager.attach(Process(name="zigate.transport", target=self.main, terminate=self._stop, log=self.log))

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
                self.log.exception('exception in transport.open()')
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
                    self.log.exception('exception in transport')
                    error = e
                else:
                    if data:
                        # make a separated try-except for called used code
                        try:
                            self.read_data(data)
                        except Exception as e:
                            self.log.exception('exception in protocol.data_received()')
                            error = e

            self._is_open = False
            dispatcher.send(DISCONNECTED, self.zigate_instance)

            if self.transport.is_open:
                try:
                    self.transport.close()
                except Exception as e:
                    self.log.exception('exception in transport.close()')

            t_end = time.time() + self.reconnect_delay
            while self._running and time.time() < t_end:
                time.sleep(1.)
            self.log.debug('reconnecting...')

    def send(self, data):
        self.transport.write(data)

    def close(self):
        if self._process:
            self._process.destroy(timeout=2)
            self._process = None


class ZigateSerial(zigate.ZiGate):
    def __init__(self, gateway, **kwargs):
        super(ZigateSerial, self).__init__(gateway.port, **kwargs)
        self.gateway = gateway

    def setup_connection(self):
        if self.connection is None:
            self.connection = WrapperConnection(self, transport=SerialTransport(self._port, 115200))


class ZigateWifi(zigate.ZiGateWiFi):
    def __init__(self, gateway, **kwargs):
        super(ZigateWifi, self).__init__(gateway.host, gateway.port, **kwargs)
        self.gateway = gateway

    def setup_connection(self):
        if self.connection is None:
            self.connection = WrapperConnection(self, transport=NetTransport(self._host, self._port))


@attr('port', type=SerialPort(), description="The serial port name.")
class ZigateSerialGateway(ZigateBaseGateway):
    RESET_ATTR = ['port']

    def _connect(self, **kwargs):
        self.log.info('zigate connect on port %s', self.port)
        return ZigateSerial(self, **kwargs)


@attr('port', type=Integer(min=0, max=65535), default=9999, description="The port number of the gateway. The default port number is 9999.")
@attr('host', type=Host(), description="The ip address or hostname of the gateway.")
class ZigateWifiGateway(ZigateBaseGateway):
    RESET_ATTR = ['host', 'port']

    def _connect(self, **kwargs):
        self.log.info('zigate connect on host %s:%s', self.host, self.port)
        return ZigateWifi(self, **kwargs)


from zigate.core import FakeZiGate


class ZigateFakeGateway(ZigateBaseGateway):

    def _connect(self, **kwargs):
        self.log.info('fake zigate connect')
        return FakeZiGate(**kwargs)

    @scheduler.delay(0, name="zigate.init")
    def _controller_start(self):
        super(ZigateFakeGateway, self)._controller_start()
        super(ZigateFakeGateway, self)._controller_init() # no CONNECTED event
