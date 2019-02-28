# coding: utf-8

from ething.core import Device
from ething.core.reg import *
from ething.core.interfaces import Relay
from ething.core import scheduler
import requests


STATE_POLLING_PERIOD = 5
REQUESTS_TIMEOUT = None


@attr('port', type=Integer(min=0, max=65535), default=80, description="The port number of the device to connect to. The default port number is 80.")
@attr('host', type=String(allow_empty=False), description="The ip address or hostname of the device to connect to.")
class Sonoff_http(Relay):
    """
    Sonoff_http Device resource representation.
    See https://github.com/arendst/Sonoff-Tasmota for more details.
    """

    def setState(self, state):
        self._make_request('GET', '/cm?cmnd=Power%%20%s' % ('On' if state else 'Off'))
        self.state = state

    @scheduler.setInterval(STATE_POLLING_PERIOD)
    def updateState(self):
        try:
            r = self._make_request('GET', '/cm?cmnd=Power', timeout=2)
            data = r.json()
            new_state = True if data.get('POWER') == 'ON' else False
            with self:
                self.setConnectState(True)
                if self.state != new_state:
                    self.state = new_state
        except:
            self.setConnectState(False)

    def _make_request(self, method, path='', params = None, body = None, headers = None, **options):

        args = dict(params=params)
        args["timeout"] = REQUESTS_TIMEOUT

        url = 'http'

        #if self.secure:
        #    url += 's'

        url += '://' + self.host

        if self.port != 80:
            url += ':' + str(self.port)

        if not path.startswith('/'):
            url += '/'

        url += path

        self.log.debug('request: %s %s' % (method, url))

        r = requests.request(method.upper(), url, headers=headers, params=params, data=body, **options)

        self.log.debug('request status: %s' % (r.status_code))

        r.raise_for_status()

        return r
