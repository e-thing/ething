# coding: utf-8
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

        setattr(cls, 'ping_host', f)
        return cls
    return d


# on windows winpcap must be installed
#def ping(host, timeout=1):
#
#    try:#
#        result = sr1(IP(dst=host)/ICMP(), timeout=timeout, verbose=False)
#    except Exception as e:
#        result = False
#
#    return bool(result)


from platform   import system as system_name  # Returns the system/OS name
from subprocess import call   as system_call  # Execute a shell command


def ping(host, **kwargs):
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