# coding: utf-8
import gevent
from .scanner import SCANNERS
from .serial import SerialScanner
from .mdns import MdnsScanner
from .ssdp import SsdpScanner
from .ble import BleaScanner


SCANNERS.add(SerialScanner)
SCANNERS.add(MdnsScanner)
SCANNERS.add(SsdpScanner)
if BleaScanner:
    SCANNERS.add(BleaScanner)


def scan(timeout=10, printer=None):
    if timeout <= 0:
        raise ValueError('timeout must be greater than 0')

    scanners = [cls() for cls in SCANNERS if cls]
    jobs = [gevent.spawn(scanner.scan, timeout) for scanner in scanners]
    gevent.joinall(jobs)

    results = sum([job.value for job in jobs if job.value], [])
    results = sum([scanner.get_results() for scanner in scanners], results)

    results = set(results)

    if printer:
        pprint_scan_results(results, printer)

    return results


def pprint_scan_results(results, printer=None):
    printer = printer or print

    # order the results
    d = dict()

    for res in results:
        type = res.type
        key = res.key
        data = res.data

        if type not in d:
            d[type] = dict()

        if key not in d[type]:
            d[type][key] = dict()

        d[type][key].update(data)

    # print it !
    if len(d) == 0:
        printer('Nothing found :-(')
    for type in d:
        printer('+ %s [len:%d] :' % (type, len(d[type])))
        for key in d[type]:
            printer('    + %s :' % (key, ))
            data = d[type][key]
            for k, v in data.items():
                printer('        - %s : %s' % (k, v))

