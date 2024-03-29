# coding: utf-8
from .. import *
from croniter import croniter
import pytz


class CronExpr(String):
    def __init__(self, **attr):
        super(CronExpr, self).__init__(allow_empty=False, **attr)

    def to_shema(self, context=None):
        schema = super(CronExpr, self).to_shema(context)
        schema['$component'] = 'cron'
        return schema


@meta(label="cron", icon='mdi-calendar-clock', category="input")
@attr('expression', label='when', type=CronExpr())
class CronNode(Node):
    """
    is emitted periodically at fixed times, dates, or intervals
    """

    OUTPUTS = ['default']

    def main(self, **inputs):

        local_tz = self.core.config.timezone
        local_ts = datetime.datetime.utcfromtimestamp(time.time())
        if local_tz != 'UTC':
            local_ts = pytz.utc.localize(local_ts).astimezone(pytz.timezone(local_tz))

        self.logger.debug('start cron node with expression %s', self.expression)
        iter = croniter(self.expression, local_ts, day_or=False)

        while True:
            next_ts = iter.get_next()
            time_to_wait = next_ts - time.time()
            self.logger.debug('wait: %s sec, next: %s', time_to_wait, next_ts)
            time.sleep(time_to_wait)
            self.emit({
                'payload': time.time()
            })
