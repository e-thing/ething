# coding: utf-8

from ething.plugins.http import HTTP
from ething.core.reg import *
from ething.core.interfaces import Switch
from ething.core import scheduler


STATE_POLLING_PERIOD = 5


@attr('secure', default=False, mode=PRIVATE)
class Sonoff_http(HTTP, Switch):
    """
    Sonoff_http Device resource representation
    """

    def setState(self, state):
        self._make_request('GET', '/cm?cmnd=Power%%20%s' % ('On' if state else 'Off'))
        self.state = state

    @scheduler.setInterval(STATE_POLLING_PERIOD, thread=True)
    def updateState(self):
        r = self._make_request('GET', '/cm?cmnd=Power')
        data = r.json()
        new_state = True if data.get('POWER') == 'ON' else False
        if self.state != new_state:
            self.state = new_state


