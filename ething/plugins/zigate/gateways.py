# coding: utf-8
import zigate
from zigate import dispatcher
from zigate.core import DeviceEncoder
from future.utils import string_types
from ething.core.Device import Device
from ething.core.reg import *
from ething.core.Process import Process
from ething.core.env import USER_DIR
from ething.core import scheduler
from .devices import zigate_device_classes
import json
import os


PERSISTENT_FILE = os.path.abspath(os.path.join(USER_DIR, 'zigate.json'))


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
            self.log.debug('save_state')
            self.z.save_state()

    @scheduler.delay(0, name="zigate.init")
    def _controller_start(self):
        self._controller_end() # just in case...

        gconf = {'auto_start':False, 'auto_save':False, 'path':self.persistent_file}

        self.z = z = self._connect(**gconf)

        #dispatcher.connect(self._controller_callback, signal=dispatcher.Any, sender=z)
        dispatcher.connect(self._controller_callback, signal=zigate.ZIGATE_DEVICE_ADDED, sender=z)
        dispatcher.connect(self._controller_callback, signal=zigate.ZIGATE_DEVICE_UPDATED, sender=z)
        dispatcher.connect(self._controller_callback, signal=zigate.ZIGATE_DEVICE_REMOVED, sender=z)
        dispatcher.connect(self._controller_callback, signal=zigate.ZIGATE_DEVICE_ADDRESS_CHANGED, sender=z)
        dispatcher.connect(self._controller_callback, signal=zigate.ZIGATE_ATTRIBUTE_ADDED, sender=z)
        dispatcher.connect(self._controller_callback, signal=zigate.ZIGATE_ATTRIBUTE_UPDATED, sender=z)
        dispatcher.connect(self._controller_callback, signal=zigate.ZIGATE_DEVICE_NEED_DISCOVERY, sender=z)

        # start
        self.log.debug('zigate startup')
        z.startup()

        self.version = z.get_version_text()
        self.log.info('zigate version: %s', self.version)

        self.addr = z.addr
        self.ieee = z.ieee
        self.channel = z.channel

    def _controller_end(self):
        if hasattr(self, 'z') and self.z:
            self.log.info('zigate close')
            self.z.save_state()
            self.z.close()
            dispatcher.disconnect(self._controller_callback, sender=self.z)
            self.z = None

    def _controller_callback(self, sender, signal, **kwargs):

        self.log.debug('signal received: %s %s', signal, kwargs)

        if 'device' in kwargs:
            dz_instance = kwargs.get('device')

            if signal == zigate.ZIGATE_DEVICE_ADDED:
                # wait for the discovery process to complete
                self.core.scheduler.delay(5., callback=lambda: self.log.info(json.dumps(dz_instance.to_json(properties=True), indent=4, sort_keys=True, cls=DeviceEncoder)))

            children = self.children(lambda r: r.ieee == dz_instance.ieee)
            if children:
                device = children[0]
            else:
                # new device
                device = self._create_device(dz_instance)

            if device:
                with device:
                    device.process_signal(signal, kwargs)

    def _create_device(self, dz_instance):
        self.log.info('new device: %s', dz_instance.info)

        for cls in zigate_device_classes:
            try:
                if cls.isvalid(self, dz_instance):
                    return cls.create_device(self, dz_instance)
            except:
                self.log.exception('zigate cls create exception')

        self.log.warning('unable to create the device: no associated class found for %s', dz_instance)

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


@attr('port', type=SerialPort(), description="The serial port name.")
class ZigateSerialGateway(ZigateBaseGateway):
    RESET_ATTR = ['port']

    def _connect(self, **kwargs):
        self.log.info('zigate connect on port %s', self.port)
        return zigate.connect(port=self.port, **kwargs)  # Leave None to auto-discover the port


@attr('port', type=Integer(min=0, max=65535), default=9999, description="The port number of the gateway. The default port number is 9999.")
@attr('host', type=Host(), description="The ip address or hostname of the gateway.")
class ZigateWifiGateway(ZigateBaseGateway):
    RESET_ATTR = ['host', 'port']

    def _connect(self, **kwargs):
        self.log.info('zigate connect on host %s:%s', self.host, self.port)
        return zigate.connect(host='%s:%s' % (self.host, self.port), **kwargs)


from zigate.core import FakeZiGate


class ZigateFakeGateway(ZigateBaseGateway):

    def _connect(self, **kwargs):
        self.log.info('fake zigate connect')
        return FakeZiGate(**kwargs)
