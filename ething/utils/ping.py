# coding: utf-8

from ething.scheduler import set_interval
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

        @set_interval(interval, name='ping')
        def _ping(self):

            host = getattr(self, attr, None)
            online = False

            if host:

                # host may be an url
                host = get_hostname(host)

                if host == 'localhost' or host == '127.0.0.1':
                    online = True
                else:
                    retry = 2 if self.connected else 1  # avoid some deconnection if the first ping fail
                    try:
                        for i in range(retry):
                            online = ping(host)
                            if online:
                                break
                    except Exception as e:
                        self.logger.error('ping() raises an exception: %s' % str(e))
                        return False

                    if not online:
                        self.logger.warning('host %s is not online', host)

                self.logger.debug('ping %s, online=%s', host, online)

            self.refresh_connect_state(online)

            return online

        setattr(cls, '_ping', _ping)
        return cls

    return d
