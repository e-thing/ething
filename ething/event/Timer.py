# coding: utf-8

from .Signal import Signal
from .Event import Event
from croniter import croniter
from ething.base import attr, isString


class Tick(Signal):
    pass



@attr('cron_expression', validator = isString(allow_empty = False))
class Timer(Event):
    """
    is emitted periodically at fixed times, dates, or intervals
    """
    signal = Tick
    
    DELTA = 2
    
    def _filter(self, signal):
        
        ts = signal.timestamp
        expr = self.cron_expression
        
        iter = croniter(expr, int(ts - self.DELTA))
        
        c = iter.get_current()
        n = iter.get_next()
        
        if n - c <= 2*self.DELTA:
            return True
        else:
            return False

