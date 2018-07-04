# coding: utf-8

from .Resource import Resource, isResource, ResourceModelAdapter
from .base import NestedAdapter, attr, READ_ONLY, isString, isAnything, isBool, isObject, isArray, isInteger
from .ScriptEngine import ScriptEngine

from . import event
from . import action
import datetime


class isEvent(isAnything):

    def schema(self):
        return {"$ref": "#/events/Event"}

class isAction(isAnything):

    def schema(self):
        return {"$ref": "#/actions/Action"}

class Adapter(NestedAdapter):
    def __init__(self):
        super(Adapter, self).__init__(event.Event)

    def _inherit(self, data_object):
        return {
            'rule': data_object
        }

class isSchedulerItem(isObject):
    
    def __init__(self):
        super(isSchedulerItem, self).__init__(start = isObject(weekDay = isInteger(min=0, max=6), hour = isInteger(min=0, max=24)), end = isObject(weekDay = isInteger(min=0, max=6), hour = isInteger(min=0, max=24)))

class isScheduler(isArray):
    
    def __init__(self):
        super(isScheduler, self).__init__(item = isSchedulerItem())


@attr('event', validator=isEvent(), model_adapter=NestedAdapter(event.Event), description="The event object describing when to execute this rule")
@attr('action', validator=isAction(), model_adapter=NestedAdapter(action.Action), description="The event object describing when to execute this rule")
@attr('enabled', validator=isBool(), default=True, description="If True (default), the rule is enabled")
@attr('scheduler', validator=isArray(item = isObject(start = isObject(weekDay = isInteger(min=0, max=6), hour = isInteger(min=0, max=24)), end = isObject(weekDay = isInteger(min=0, max=6), hour = isInteger(min=0, max=24)))), default=[], description="Activate this rule only within certain periods of time")
@attr('execution_count', default=0, mode=READ_ONLY, description="The number of times this rule has been executed")
@attr('execution_date', default=None, mode=READ_ONLY, description="The last time this rule has been executed")
class Rule(Resource):

    def trigger(self, signal):

        if not self.event.filter(signal):
            return False

        return self.run(signal)
    
    def _generateShedulerTimeIndex(weekDay, hour):
        return (weekDay * 100) + hour
    
    @property
    def is_active(self):
        
        if self.enabled:
            
            if self.scheduler:
                
                now = datetime.datetime.now()
                weekday = now.weekday()
                hour = now.hour
                t = self._generateShedulerTimeIndex(weekday, hour)
                
                for item in self.scheduler:
                    
                    start = item.get('start', {})
                    end = item.get('end', {})
                    
                    t_start = self._generateShedulerTimeIndex(start.get('weekDay', 0), start.get('hour', 0))
                    t_end = self._generateShedulerTimeIndex(end.get('weekDay', 0), end.get('hour', 0))
                    
                    if t >= t_start and t < t_end:
                        return True
                
                return False
            
            return True
        
        return False

    def run(self, signal=None):

        self._execution_count = self.execution_count + 1

        self._execution_date = datetime.datetime.utcnow()

        try:
            self.action.run(signal)
        except Exception as e:
            self.ething.log.exception('error while running the action of the rule %s' % self)

        self.save()

