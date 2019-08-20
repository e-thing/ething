# coding: utf-8

import socket
import subprocess
import re
import sys
from multiping import multi_ping, MultiPingError
import requests
import time
from platform import system as system_name  # Returns the system/OS name
import logging


# _LOGGER = logging.getLogger('net_scan')


def get_my_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    ip = s.getsockname()[0]
    s.close()
    return ip


arp_ip_mac_re_win = re.compile(r'^\s*([0-9\.]+)\s+([0-9a-fA-F\-:]+)\s')
arp_ip_mac_re_unix = re.compile(r'\(([0-9\.]+)\)\s+at\s+([0-9a-fA-F\-:]+)\s')


def read_arp_table():
    arp_map = {}

    if system_name().lower() == 'windows':
        arp_ip_mac_re = arp_ip_mac_re_win
        args = ["arp", "-a"]
    else:
        arp_ip_mac_re = arp_ip_mac_re_unix
        args = ["arp", "-an"]

    try:
        out = subprocess.check_output(args)

        if out:
            out = out.decode(sys.stdout.encoding or 'utf8', errors="ignore")

            for line in out.splitlines():
                matches = arp_ip_mac_re.search(line)
                if matches:
                    ip = matches.group(1)
                    mac = matches.group(2)

                    arp_map[ip] = mac.replace('-', ':')
    except:
        pass

    return arp_map


def get_vendor_from_mac(mac, retries=3):

    vendor = None
    i=0

    while i<retries:
        r = requests.get('https://api.macvendors.com/%s' % mac.replace(':', '-'))

        if r.status_code == 200:
            vendor = r.text
            break
        elif r.status_code == 429:
            # need to wait before retry
            time.sleep(0.5)
        else:
            break

    return vendor


_cache_mac_vendor = {}
_cache_scan = {}

SCAN_CACHE_VALIDITY = 10


def scan(force=False, cache_validity=SCAN_CACHE_VALIDITY):

    # check cache
    if not force:
        cache_ts = _cache_scan.get('ts')
        if cache_ts and time.time() - cache_ts <= cache_validity:
            return _cache_scan.get('results')

    results = []

    # get my IP and compose a base like 192.168.1.xxx
    myip = get_my_ip() or '192.168.1.0'
    ip_parts = myip.split('.')
    base_ip = ip_parts[0] + '.' + ip_parts[1] + '.' + ip_parts[2] + '.'

    # _LOGGER.debug('myip = %s , base_ip = %s' % (myip,base_ip))

    ips = []
    for i in range(1, 255):
        ips.append(base_ip + '{0}'.format(i))

    try:
        res, _ = multi_ping(ips, timeout=1)
    except MultiPingError:
        # need root privileges
        return results

    ip_detected = list(res.keys())

    # _LOGGER.debug('ip detected: %s' % (ip_detected))

    arp_map = read_arp_table()

    # _LOGGER.debug('arp_map: %s' % (arp_map))

    for ip in ip_detected:

        # _LOGGER.debug('process ip: %s' % (ip))

        # get its mac address
        mac = arp_map.get(ip)
        vendor = None

        if mac:
            # get vendor information
            if mac in _cache_mac_vendor:
                vendor = _cache_mac_vendor.get(mac)
            else:
                vendor = get_vendor_from_mac(mac)
                _cache_mac_vendor[mac] = vendor

        results.append({
            'ip': ip,
            'mac': mac,
            'vendor': vendor,
            'is_localhost': ip == myip
        })

    _cache_scan['results'] = results
    _cache_scan['ts'] = time.time()

    return results


if __name__ == '__main__':
    results = scan()

    print(results)
