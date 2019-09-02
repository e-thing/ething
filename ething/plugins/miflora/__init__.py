# coding: utf-8

from miflora.miflora_poller import MiFloraPoller, MI_BATTERY, MI_TEMPERATURE, MI_LIGHT, MI_MOISTURE, MI_CONDUCTIVITY
from miflora.miflora_scanner import VALID_DEVICE_NAMES, DEVICE_PREFIX
from ething.Device import BleDevice
from ething.reg import *
from ething.interfaces import Thermometer, LightSensor, MoistureSensor, sensor_attr
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


PARAMS = (MI_BATTERY, MI_TEMPERATURE, MI_LIGHT, MI_MOISTURE, MI_CONDUCTIVITY)


def install(core, options):

    def discover_handler(alive, info):
        mac = info.get('mac')
        name = info.get('name')

        if (name is not None and name.lower() in VALID_DEVICE_NAMES) or mac.upper().startswith(DEVICE_PREFIX):
            if alive:
                dev = core.find_one(lambda r: r.typeof(MiFlora) and r.address == mac)
                if not dev:
                    # not already created, so create it !
                    dev = core.create(MiFlora, {
                        'name': 'MiFlora',
                        'address': mac
                    })
                if dev:
                    # update rssi
                    dev.rssi = info.get('rssi')

    ble.register(discover_handler)


@sensor_attr('conductivity', type = Number(), default = 0, unit='µS/cm', description = "the conductivity of the soil measured by this sensor.")
@attr('firmware', default=None, mode=READ_ONLY, description="The firmware version of this device.")
class MiFlora(BleDevice, Thermometer, LightSensor, MoistureSensor):


    def __init__(self, *args, **kwargs):
        super(MiFlora).__init__(*args, **kwargs)

        self._poller = MiFloraPoller(
            self.address,
            adapter='hci%d' % self.hci,
            backend=backend,
        )

    @scheduler.set_interval(READ_INTERVAL, name="miflora.update")
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
                elif param == MI_LIGHT:
                    if data is not False:
                        rec = True
                        self.light_level = value
                elif param == MI_MOISTURE:
                    rec = True
                    self.moisture = value
                elif param == MI_CONDUCTIVITY:
                    rec = True
                    self.conductivity = value

            self.refresh_connect_state(rec)

