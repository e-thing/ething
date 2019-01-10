# coding: utf-8

from . import Signal, Event
from croniter import croniter
from ...reg import attr, String, meta
import pytz
import datetime

__all__ = ["Tick", "Timer"]


class Tick(Signal):
    pass


class CronExpr(String):
    def __init__(self, **attributes):
        super(CronExpr, self).__init__(allow_empty=False, **attributes)

    def toSchema(self, context=None):
        schema = super(CronExpr, self).toSchema(context)
        schema['format'] = 'cron'
        return schema


@meta(icon='mdi-clock-outline')
@attr('cron_expression', type=CronExpr())
class Timer(Event):
    """
    is emitted periodically at fixed times, dates, or intervals
    """
    signal = Tick

    DELTA = 2

    def _filter(self, signal, core):

        ts = signal.timestamp
        expr = self.cron_expression

        local_tz = core.config.get('timezone', 'UTC')
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

        # self.log.debug("expr: %s, ts: %d, date: %s, c: %d, n: %d" % (expr, ts, local_ts, c, n))

        if abs(n - c) <= 2*self.DELTA:
            return True
        else:
            return False
