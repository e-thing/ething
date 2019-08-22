# coding: utf-8
from .. import *


def item_to_daily_time(hour, minute):
    return hour * 3600 + minute * 60

def item_to_weekly_time(weekday, hour, minute):
    if weekday == 0:
        weekday = 7
    return weekday * 86400 + hour * 3600 + minute * 60

def item_to_monthly_time(monthday, hour, minute):
    return monthday * 86400 + hour * 3600 + minute * 60


SchedulerDataItem = Dict(
    optionals = ('monthday', 'weekday'),
    mapping = {
        'monthday': Integer(min=1, max=31),
        'weekday': Integer(min=1, max=7),
        'hour': Integer(min=0, max=23),
        'minute': Integer(min=0, max=59)
    }
)


class SchedulerData(Array):
    def __init__(self, **attributes):
        super(SchedulerData, self).__init__(
            Dict(
                mapping=OrderedDict([
                    ('mode', Enum(['daily', 'weekly', 'monthly'])),
                    ('start', SchedulerDataItem),
                    ('end', SchedulerDataItem)
                ])
            ),
            min_len=1,
            **attributes
        )

    def to_shema(self, context = None):
        schema = super(SchedulerData, self).to_shema(context)
        schema['$component'] = 'scheduler'
        return schema


@meta(icon='mdi-clock-outline', category="condition")
@attr('items', type=SchedulerData())
class Scheduler(Node):
    """ Return true only within certain periods of time """

    INPUTS = ['default']
    OUTPUTS = ['default', 'fail']

    def main(self, **inputs):
        msg = inputs.get('default')

        now = datetime.datetime.now()
        weekday = now.isoweekday() # 1: monday, 7: sunday
        hour = now.hour
        minute = now.minute
        monthday = now.day
        res = False

        for item in self.items:

            mode = item.get('mode')
            start = item.get('start')
            end = item.get('end')

            if mode == 'daily':
                start_time = item_to_daily_time(start.get('hour'), start.get('minute'))
                end_time = item_to_daily_time(end.get('hour'), end.get('minute'))
                time = item_to_daily_time(hour, minute)

            elif mode == 'weekly':
                start_time = item_to_weekly_time(start.get('weekday'), start.get('hour'), start.get('minute'))
                end_time = item_to_weekly_time(end.get('weekday'), end.get('hour'), end.get('minute'))
                time = item_to_weekly_time(weekday, hour, minute)

            elif mode == 'monthday':
                start_time = item_to_weekly_time(start.get('monthday'), start.get('hour'), start.get('minute'))
                end_time = item_to_weekly_time(end.get('monthday'), end.get('hour'), end.get('minute'))
                time = item_to_weekly_time(monthday, hour, minute)
            else:
                continue

            if start_time <= end_time:
                if time >= start_time and time <= end_time:
                    res = True
                    break
            else:
                if time >= start_time or time <= end_time:
                    res = True
                    break

        self.emit(msg, port='default' if res else 'fail')

