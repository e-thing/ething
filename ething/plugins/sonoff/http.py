# coding: utf-8

from ething.plugins.http import HTTP
from ething.core.reg import *
from ething.core.interfaces import Switch
#from ething.core.Scheduler import setInterval


STATE_POLLING_PERIOD = 10


@attr('secure', default=False, mode=PRIVATE)
class Sonoff_http(HTTP, Switch):
    """
    Sonoff_http Device resource representation
    """

    def setState(self, state):
        self._make_request('GET', '/cm?cmnd=Power%%20%s' % ('On' if state else 'Off'))
        self.state = state


    #@setInterval(STATE_POLLING_PERIOD)
    def updateState(self):
        r = self._make_request('GET', '/cm?cmnd=Power')
        data = r.json()
        self.state = True if data.get('state') == 'On' else False


