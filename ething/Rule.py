# coding: utf-8

from .Resource import Resource
from .base import NestedArrayAdapter, attr, READ_ONLY, isAnything, isBool, isObject, isArray, isInteger

from . import event
from . import action
import datetime


class isEvent(isAnything):

    def schema(self):
        return {"$ref": "#/events/Event"}

class isAction(isAnything):

    def schema(self):
        return {"$ref": "#/actions/Action"}

class isSchedulerItem(isObject):
    
    def __init__(self):
        super(isSchedulerItem, self).__init__(start = isObject(weekDay = isInteger(min=0, max=6), hour = isInteger(min=0, max=24)), end = isObject(weekDay = isInteger(min=0, max=6), hour = isInteger(min=0, max=24)))

class isScheduler(isArray):
    
    def __init__(self):
        super(isScheduler, self).__init__(item = isSchedulerItem())

@attr('actions', validator=isArray(item = isAction(), min_len = 1), model_adapter=NestedArrayAdapter(action.Action), description="A list of actions describing a flow. Actions will be executed one after another.")
@attr('events', validator=isArray(item = isEvent(), min_len = 1), model_adapter=NestedArrayAdapter(event.Event), description="A list of events describing when to execute this rule.")
@attr('enabled', validator=isBool(), default=True, description="If True (default), the rule is enabled")
@attr('scheduler', validator=isArray(item = isObject(start = isObject(weekDay = isInteger(min=0, max=6), hour = isInteger(min=0, max=24)), end = isObject(weekDay = isInteger(min=0, max=6), hour = isInteger(min=0, max=24)))), default=[], description="Activate this rule only within certain periods of time")
@attr('execution_count', default=0, mode=READ_ONLY, description="The number of times this rule has been executed")
@attr('execution_date', default=None, mode=READ_ONLY, description="The last time this rule has been executed")
class Rule(Resource):
    """
    Rule dictate the action to perform when an event occurs.
    Rules consist of two parts:
     - The event part specifies the conditions that triggers the invocation of the rule
     - The action part specifies what to execute in response to the event
    """

    def signal_match(self, signal):
        with self:
            events = self.events
            dopass = False

            for i in range(len(events)):
                try:
                    event = events[i]
                    if event.filter(signal):
                        dopass = True
                except Exception as e:
                    self.ething.log.exception('error while filtering the event[%d] %s of the rule %s' % (i, event, self))

            return dopass

    def trigger(self, signal):

        with self:
            if not self.signal_match(signal):
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

        actions = self.actions

        for i in range(len(actions)):
            try:
                action = actions[i]
                action.run(signal)
            except Exception as e:
                self.ething.log.exception('error while running the action[%d] %s of the rule %s' % (i, action, self))
                break

        self.save()

