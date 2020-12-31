# coding: utf-8

from .mitemp_bt_poller import MiTempBtPoller, MI_BATTERY, MI_TEMPERATURE, MI_HUMIDITY
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
        elif name is not None and name.upper() == 'LYWSD03MMC':
            if alive:
                dev = core.find_one(lambda r: r.typeof(LYWSD03MMC) and r.address == mac)
                if not dev:
                    # not already created, so create it !
                    dev = core.create(LYWSD03MMC, {
                        'name': 'Mijia LYWSD03MMC',
                        'address': mac
                    })
                if dev:
                    # update rssi
                    dev.rssi = info.get('rssi')

    ble.register(discover_handler)


@attr('firmware', default=None, mode=READ_ONLY, description="The firmware version of this device.")
@meta(disable_creation=True)
class Mijia(BleDevice, Thermometer, HumiditySensor):


    def __init__(self, *args, **kwargs):
        super(Mijia, self).__init__(*args, **kwargs)

        self._poller = MiTempBtPoller(
            self.address,
            backend,
            adapter=('hci%d' % self.hci)
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


@meta(disable_creation=True)
class LYWSD03MMC(BleDevice, Thermometer, HumiditySensor):

    def __init__(self, *args, **kwargs):
        super(LYWSD03MMC, self).__init__(*args, **kwargs)

    def handleNotification(self, cHandle, data):
        try:
            temp = int.from_bytes(data[0:2], byteorder='little', signed=True) / 100
            temp = round(temp, 1)

            humidity = int.from_bytes(data[2:3], byteorder='little')
            voltage = int.from_bytes(data[3:5], byteorder='little') / 1000.

            batteryLevel = min(int(round((voltage - 2.1), 2) * 100), 100)  # 3.1 or above --> 100% 2.1 --> 0 %
            if batteryLevel < 0:
                batteryLevel = 0

            with self:
                self.battery = batteryLevel
                self.temperature = temp
                self.humidity = humidity
                self.refresh_connect_state(True)

        except Exception as e:
            self.logger.exception(e)

    @scheduler.set_interval(READ_INTERVAL, name="LYWSD03MMC.update")
    def _update(self):

        success = False
        for i in range(5):
            p = None

            try:
                p = bluepy.btle.Peripheral(self.address, iface=self.hci)

                val = b'\x01\x00'
                p.writeCharacteristic(0x0038, val,
                                      True)  # enable notifications of Temperature, Humidity and Battery voltage
                # p.writeCharacteristic(0x0046, b'\xf4\x01\x00', True)  # enable lower power mode, please don't do when you want to interact with the device, because often then connection gets lost
                p.withDelegate(self)

                if p.waitForNotifications(2000):
                    success = True
                    break

            except bluepy.btle.BTLEDisconnectError as e:
                pass

            if p is not None:
                p.disconnect()

        if not success:
            self.refresh_connect_state(False)

