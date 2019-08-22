# coding: utf-8
from ..type import Date
from datetime import datetime
import pytz
from dateparser import parse as _parse



get_local_tz_from_context = lambda context: context['core'].local_tz


class TzDate(Date):
    def __init__(self, **attributes):
        super(TzDate, self).__init__(ignore_tz=False, tz=pytz.utc, from_tz=get_local_tz_from_context, to_tz=get_local_tz_from_context, **attributes)


def utcnow():
    return datetime.utcnow().replace(tzinfo=pytz.utc)


def utcfromtimestamp(timestamp):
    return datetime.utcfromtimestamp(timestamp).replace(tzinfo=pytz.utc)


def datetime_to_array(dt):
    return [dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second]


def parse(d, tz):
    """return datetime object in UTC"""
    return _parse(
        d,
        languages=['en'],
        settings={
            'TIMEZONE': tz,
            'TO_TIMEZONE': 'UTC',
            'RETURN_AS_TIMEZONE_AWARE': True
        }
    )
