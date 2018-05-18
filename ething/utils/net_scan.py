# coding: utf-8
#cf. https://github.com/bwaldvogel/neighbourhood/blob/master/neighbourhood.py

from __future__ import absolute_import, division, print_function
import scapy.layers.l2
import scapy.config
import scapy.route
import math
import errno
import socket
import requests


def long2net(arg):
    if (arg <= 0 or arg >= 0xFFFFFFFF):
        raise ValueError("illegal netmask value", hex(arg))
    return 32 - int(round(math.log(0xFFFFFFFF - arg, 2)))


def to_CIDR_notation(bytes_network, bytes_netmask):
    network = scapy.utils.ltoa(bytes_network)
    netmask = long2net(bytes_netmask)
    net = "%s/%s" % (network, netmask)
    if netmask < 16:
        return None

    return net

def scan_and_print_neighbors(net, interface, timeout=1):
    results = []
    # print("arping %s on %s" % (net, interface))
    try:
        ans, unans = scapy.layers.l2.arping(net, iface=interface, timeout=timeout, verbose=False)
        for s, r in ans.res:
            mac=r.src
            ip=r.psrc
            hostname = ''
            try:
                tup = socket.gethostbyaddr(r.psrc)
                hostname = tup[0]
            except socket.herror:
                # failed to resolve
                pass
            
            vendor = get_vendor(mac)
            
            # print(ip, mac, hostname, vendor)
            
            results.append({
                'mac': mac,
                'ip': ip,
                'hostname': hostname,
                'vendor': vendor
            })
            
    except socket.error as e:
        if e.errno == errno.EPERM:     # Operation not permitted
            #print("%s. Did you run as root?", e.strerror)
            pass
        else:
            raise
    return results


_vendor_cache = {}

def get_vendor(mac):
    
    if mac in _vendor_cache:
        return _vendor_cache[mac]
    
    try:
        url = 'http://api.macvendors.com/' + mac
        r = requests.get(url)
        if r.status_code == 200:
            _vendor_cache[mac] = r.text
            return r.text
    except Exception as e:
        pass
    return ""



def scan():
    results = []
    
    for route in scapy.config.conf.route.routes:
        
        network = route[0]
        netmask = route[1]
        interface = route[3]
        address = route[4]
        
        # skip loopback network and default gw
        if network == 0 or interface == 'lo' or address == '127.0.0.1' or address == '0.0.0.0':
            continue

        if netmask <= 0 or netmask == 0xFFFFFFFF:
            continue
        
        if interface != scapy.config.conf.iface:
            # see http://trac.secdev.org/scapy/ticket/537
            # skipping because scapy currently doesn't support arping on non-primary network interfaces
            continue
        
        net = to_CIDR_notation(network, netmask)
        
        if net:
            # print(network, netmask, interface, address, net)
            r = scan_and_print_neighbors(net, interface)
            results += r
    
    return results

