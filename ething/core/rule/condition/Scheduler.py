# coding: utf-8

from .Condition import Condition
from ething.core.entity import *
import datetime



def item_to_daily_time(hour, minute):
    return hour * 3600 + minute * 60

def item_to_weekly_time(weekday, hour, minute):
    if weekday == 0:
        weekday = 7
    return weekday * 86400 + hour * 3600 + minute * 60

def item_to_monthly_time(monthday, hour, minute):
    return monthday * 86400 + hour * 3600 + minute * 60


@attr('items', type=Array(Dict(mapping = OrderedDict([('mode', Enum(['daily', 'weekly', 'monthly'])), ('start', Dict(optionals = ('monthday', 'weekday'), mapping = {'monthday': Integer(min=1, max=31), 'weekday': Integer(min=1, max=7), 'hour': Integer(min=0, max=23), 'minute': Integer(min=0, max=59)})), ('end', Dict(optionals = ('monthday', 'weekday'), mapping = {'monthday': Integer(min=1, max=31), 'weekday': Integer(min=1, max=7), 'hour': Integer(min=0, max=23), 'minute': Integer(min=0, max=59)}))])), min_len=1))
class Scheduler(Condition):
    """ Activate this rule only within certain periods of time """
    def test(self, signal):
        now = datetime.datetime.now()
        weekday = now.isoweekday() # 1: monday, 7: sunday
        hour = now.hour
        minute = now.minute
        monthday = now.day

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
                    return True
            else:
                if time >= start_time or time <= end_time:
                    return True



