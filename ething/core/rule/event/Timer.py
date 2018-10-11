# coding: utf-8

from . import Signal, Event
from croniter import croniter
from ...reg import attr, String
import pytz
import datetime

__all__ = ["Tick", "Timer"]


class Tick(Signal):
    pass


@attr('cron_expression', type=String(allow_empty=False))
class Timer(Event):
    """
    is emitted periodically at fixed times, dates, or intervals
    """
    signal = Tick

    DELTA = 2

    def _filter(self, signal):

        ts = signal.timestamp
        expr = self.cron_expression

        local_tz = self.ething.config.get('timezone', 'UTC')
        local_ts = datetime.datetime.utcfromtimestamp(ts - self.DELTA)
        if local_tz != 'UTC':
            local_ts = pytz.utc.localize(local_ts).astimezone(pytz.timezone(local_tz))

        iter = croniter(expr, local_ts, day_or=False)

        c = iter.get_current()
        n = iter.get_next()

        for _ in range(5):
            if n >= c:
                break
            n = iter.get_next()

        # self.ething.log.debug("expr: %s, ts: %d, date: %s, c: %d, n: %d" % (expr, ts, local_ts, c, n))

        if abs(n - c) <= 2*self.DELTA:
            return True
        else:
            return False
