# coding: utf-8
from . import get_lock, init_iface
from bluepy.btle import Peripheral, BTLEException
import time
import logging


# bluepy patch to avoid device disconnect infinite loop
def disconnect(self):
    if self._helper is None:
        return
        # Unregister the delegate first
    self.setDelegate(None)

    self._writeCmd("disc\n")
    self._getResp('stat', 5)
    self._stopHelper()

Peripheral.disconnect = disconnect


_LOGGER = logging.getLogger(__name__)
RETRY_LIMIT = 3
RETRY_DELAY = 0.1


def wrap_exception(func):
    """Decorator to wrap BTLEExceptions into BluetoothBackendException."""

    def _func_wrapper(*args, **kwargs):
        error_count = 0
        last_error = None
        while error_count < RETRY_LIMIT:
            try:
                return func(*args, **kwargs)
            except BTLEException as exception:
                error_count += 1
                last_error = exception
                time.sleep(RETRY_DELAY)
                _LOGGER.debug('Call to %s failed, try %d of %d', func, error_count, RETRY_LIMIT)
        raise last_error

    return _func_wrapper


class Connector(object):
    def __init__(self, iface, mac):
        self._iface = iface
        self._mac = mac
        self._peripheral = None
        self._lock = get_lock(iface)
    
    def __enter__(self):
        self.connect()
        return self
    
    def __exit__(self, type, value, traceback):
        self.disconnect()

    @wrap_exception
    def connect(self):
        """Connect to a device."""
        try:
            self._lock.acquire()
            init_iface(self._iface)
            self._peripheral = Peripheral(self._mac, iface=self._iface)
        except:
            self._lock.release()
            raise

    @wrap_exception
    def disconnect(self):
        """Disconnect from a device if connected."""
        try:
            if self._peripheral is not None:
                self._peripheral.disconnect()
                self._peripheral = None
        finally:
            self._lock.release()

    @wrap_exception
    def read_handle(self, handle):
        """Read a handle from the device.
        You must be connected to do this.
        """
        if self._peripheral is None:
            raise Exception('not connected to backend')
        return self._peripheral.readCharacteristic(handle)

    @wrap_exception
    def write_handle(self, handle, value):
        """Write a handle from the device.
        You must be connected to do this.
        """
        if self._peripheral is None:
            raise Exception('not connected to backend')

        return self._peripheral.writeCharacteristic(handle, value, True)

    @wrap_exception
    def wait_for_notification(self, handle, delegate, notification_timeout):
        if self._peripheral is None:
            raise Exception('not connected to backend')
        self.write_handle(handle, bytearray([0x01, 0x00]))
        self._peripheral.withDelegate(delegate)
        return self._peripheral.waitForNotifications(notification_timeout)

