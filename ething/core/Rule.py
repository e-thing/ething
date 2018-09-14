# coding: utf-8

from .Resource import Resource
from .entity import *

from . import event
from . import condition
from . import action
import datetime


@attr('enabled', type=Boolean(), default=True, description="If True (default), the rule is enabled")
@attr('actions', type=Array(action.Action, min_len = 1), description="A list of actions describing a flow. Actions will be executed one after another.")
@attr('conditions', type=Array(condition.Condition, min_len = 0), default=[], description="A list of conditions. All conditions must match to execute this rule.")
@attr('events', type=Array(event.Event, min_len = 1), description="A list of events describing when to execute this rule.")
# @attr('scheduler', type=Array(Dict(mapping = { 'start': Dict(mapping = { 'weekDay': Integer(min=0, max=6), 'hour': Integer(min=0, max=24) }), 'end': Dict(mapping = { 'weekDay': Integer(min=0, max=6), 'hour': Integer(min=0, max=24) })})), default=[], description="Activate this rule only within certain periods of time")
@attr('execution_count', default=0, mode=READ_ONLY, description="The number of times this rule has been executed")
@attr('execution_date', default=None, mode=READ_ONLY, description="The last time this rule has been executed")
class Rule(Resource):
    """
    Rule dictate the action to perform when an event occurs.
    Rules consist of three parts:
     - The event part specifies the conditions that triggers the invocation of the rule
     - The condition part is a logical test that, if satisfied or evaluates to true, causes the action to be carried out
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

    def condition_match(self, signal):
        with self:
            conditions = self.conditions

            if len(conditions) == 0:
                return True

            dopass = False

            for i in range(len(conditions)):
                try:
                    condition = conditions[i]
                    if condition.test(signal):
                        dopass = True
                        break
                except Exception as e:
                    self.ething.log.exception('error while testing the condition[%d] %s of the rule %s' % (i, condition, self))

            return dopass

    def trigger(self, signal):

        with self:
            if not self.signal_match(signal):
                return False

            if not self.condition_match(signal):
                return False

            return self.run(signal)
    
    # def _generateShedulerTimeIndex(weekDay, hour):
    #      return (weekDay * 100) + hour
    
    @property
    def is_active(self):
        
        if self.enabled:
            
            # if self.scheduler:
            #
            #     now = datetime.datetime.now()
            #     weekday = now.weekday()
            #     hour = now.hour
            #     t = self._generateShedulerTimeIndex(weekday, hour)
            #
            #     for item in self.scheduler:
            #
            #         start = item.get('start', {})
            #         end = item.get('end', {})
            #
            #         t_start = self._generateShedulerTimeIndex(start.get('weekDay', 0), start.get('hour', 0))
            #         t_end = self._generateShedulerTimeIndex(end.get('weekDay', 0), end.get('hour', 0))
            #
            #         if t >= t_start and t < t_end:
            #             return True
            #
            #     return False
            
            return True
        
        return False

    def run(self, signal=None):

        with self:
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

