# coding: utf-8

from mitemp_bt.mitemp_bt_poller import MiTempBtPoller, MI_BATTERY, MI_TEMPERATURE, MI_HUMIDITY
from ething.Device import BleDevice
from ething.reg import *
from ething.interfaces import Thermometer, HumiditySensor
from ething import scheduler
from btlewrap import BluetoothBackendException
from ething.discovery import ble


READ_INTERVAL = 300


try:
    import bluepy.btle
    from btlewrap import BluepyBackend

    backend = BluepyBackend
except ImportError:
    from btlewrap import GatttoolBackend

    backend = GatttoolBackend


PARAMS = (MI_BATTERY, MI_TEMPERATURE, MI_HUMIDITY)


def install(core, options):

    def discover_handler(alive, info):
        mac = info.get('mac')
        name = info.get('name')

        if name is not None and name.upper().startswith('MJ_HT_'):
            if alive:
                dev = core.find_one(lambda r: r.typeof(Mijia) and r.address == mac)
                if not dev:
                    # not already created, so create it !
                    dev = core.create(Mijia, {
                        'name': 'Mijia BT Hygrothermograph',
                        'address': mac
                    })
                if dev:
                    # update rssi
                    dev.rssi = info.get('rssi')

    ble.register(discover_handler)


@attr('firmware', default=None, mode=READ_ONLY, description="The firmware version of this device.")
class Mijia(BleDevice, Thermometer, HumiditySensor):


    def __init__(self, *args, **kwargs):
        super(Mijia).__init__(*args, **kwargs)

        self._poller = MiTempBtPoller(
            self.address,
            adapter='hci%d' % self.hci,
            backend=backend,
        )

    @scheduler.set_interval(READ_INTERVAL, name="mijia.update")
    def update_data(self):

        data = dict()

        self._poller.clear_cache()

        for param in PARAMS:

            try:
                self.logger.debug("Polling data for param=%s", param)
                d = self._poller.parameter_value(param)
            except IOError as ioerr:
                self.logger.info("Polling error %s", ioerr)
                break
            except BluetoothBackendException as bterror:
                self.logger.info("Polling error %s", bterror)
                break

            if d is not None:
                data[param] = d
            else:
                self.logger.info("Did not receive any data for param=%s", param)
                break

        with self:

            rec = False
            for param in data:
                value = data[param]
                if param == MI_BATTERY:
                    self.battery = value
                    if not self.firmware:
                        self.firmware = self._poller.firmware_version()
                elif param == MI_TEMPERATURE:
                    rec = True
                    self.temperature = value
                elif param == MI_HUMIDITY:
                    rec = True
                    self.humidity = value

            self.refresh_connect_state(rec)

