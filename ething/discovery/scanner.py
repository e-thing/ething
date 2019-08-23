# coding: utf-8
from queue import Queue, Empty


SCANNERS = set()


class Scanner(object):

    def __init__(self):
        self.results = Queue()

    def scan(self, timeout):
        """
        perform the scan.

        :param timeout: timeout parameter
        :return: either fill self.results or return the results.
        """
        raise NotImplementedError

    def get_results(self):
        results = list()
        while True:
            try:
                results.append(self.results.get(False))
            except Empty:
                break
        return results


class ScannerResult(object):

    def __init__(self, key, type, data=None):
        self._key = key
        self._type = type
        self._data = data or dict()

    @property
    def key(self):
        return self._key

    @property
    def type(self):
        return self._type

    @property
    def data(self):
        return self._data

    def __json__(self):
        return {
            'key': self.key,
            'type': self.type,
            'data': self.data,
        }


class NetScannerResult(ScannerResult):
    def __init__(self, ip, data=None):
        super(NetScannerResult, self).__init__(ip, 'NET', data)


class SerialScannerResult(ScannerResult):
    def __init__(self, device, data=None):
        super(SerialScannerResult, self).__init__(device, 'SERIAL', data)


class BleaScannerResult(ScannerResult):
    def __init__(self, mac, data=None):
        super(BleaScannerResult, self).__init__(mac, 'BLUETOOTH', data)

