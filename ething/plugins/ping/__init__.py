# coding: utf-8

from ething.core import scheduler
from platform import system as system_name  # Returns the system/OS name
from subprocess import call as system_call  # Execute a shell command

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


def pingable(attr='host', interval=PING_DEFAULT_INTERVAL):
    def d(cls):

        @scheduler.setInterval(interval, thread=True)
        def ping(self):

            host = getattr(self, attr, None)
            online = False

            if host:

                # host may be an url
                host = get_hostname(host)

                if host == 'localhost' or host == '127.0.0.1':
                    online = True
                else:
                    online = _ping(host)
                    self.log.debug('ping %s, online=%s' % (host, online))

            with self:
                self.setConnectState(online)

            return online

        setattr(cls, 'ping', ping)
        return cls

    return d


def _ping(host):
    """
    Returns True if host (str) responds to a ping request.
    Remember that a host may not respond to a ping (ICMP) request even if the host name is valid.
    """

    # Ping command count option as function of OS
    param = '-n' if system_name().lower()=='windows' else '-c'

    # Building the command. Ex: "ping -c 1 google.com"
    command = ['ping', param, '1', host]

    # Pinging
    return system_call(command, stdout=False, stderr=False) == 0


