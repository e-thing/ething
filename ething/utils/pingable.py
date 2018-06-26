# coding: utf-8
from scapy.sendrecv import sr1
from scapy.layers.inet import IP, ICMP
try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse

def pingable(attr='host'):
    def d(cls):
        def f(self, *args, **kwargs):

            host = getattr(self, attr, None)
            online = False

            if host:
                
                # host may be an url
                if '/' in host:
                    if '//' not in host:
                        host = '//' + host
                    host = urlparse(host).hostname
                
                if host == 'localhost' or host == '127.0.0.1':
                    online = True
                else:
                    online = ping(host, *args, **kwargs)

            self.setConnectState(online)

            return online

        setattr(cls, 'ping', f)
        return cls
    return d


def ping(host, timeout=1):

    try:
        result = sr1(IP(dst=host)/ICMP(), timeout=timeout, verbose=False)
    except:
        result = False

    return bool(result)
