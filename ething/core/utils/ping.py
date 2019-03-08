# coding: utf-8

from ething.core import scheduler
from multiping import multi_ping
try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse


PING_DEFAULT_INTERVAL = 60


def get_hostname(url):
    # host may be an url
    if '/' in url:
        if '//' not in url:
            url = '//' + url
        return urlparse(url).hostname
    return url


def ping(host):
    """
    Returns True if host (str) responds to a ping request.
    Remember that a host may not respond to a ping (ICMP) request even if the host name is valid.
    """
    results, no_results = multi_ping([host], 1)
    return bool(results)


def pingable(attr='host', interval=PING_DEFAULT_INTERVAL):
    def d(cls):

        @scheduler.setInterval(interval, name='ping')
        def _ping(self):

            host = getattr(self, attr, None)
            online = False

            if host:

                # host may be an url
                host = get_hostname(host)

                if host == 'localhost' or host == '127.0.0.1':
                    online = True
                else:
                    try:
                        online = ping(host)
                    except Exception as e:
                        self.log.error('ping() raises an exception: %s' % str(e))
                        return False

                self.log.debug('ping %s, online=%s' % (host, online))

            with self:
                self.setConnectState(online)

            return online

        setattr(cls, 'ping', _ping)
        return cls

    return d





