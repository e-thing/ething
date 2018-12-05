# coding: utf-8

from ething.plugins.http import HTTP
from ething.core.reg import *
from ething.core.interfaces import Switch
from ething.core import scheduler


STATE_POLLING_PERIOD = 5


@attr('secure', default=False, mode=PRIVATE)
class Sonoff_http(HTTP, Switch):
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


