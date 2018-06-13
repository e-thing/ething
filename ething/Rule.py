# coding: utf-8

from .Resource import Resource, isResource, ResourceModelAdapter
from .base import NestedAdapter, attr, READ_ONLY, isString, isAnything, isBool, isObject, isArray, isInteger
from .ScriptEngine import ScriptEngine

from . import event
import datetime


class isEvent(isAnything):

    def schema(self):
        return {"$ref": "#/events/Event"}


class EventAdapter(NestedAdapter):
    def __init__(self):
        super(EventAdapter, self).__init__(event.Event)

    def _inherit(self, data_object):
        return {
            'ething': data_object.ething
        }

class isSchedulerItem(isObject):
    
    def __init__(self):
        super(isSchedulerItem, self).__init__(start = isObject(weekDay = isInteger(min=0, max=6), hour = isInteger(min=0, max=24)), end = isObject(weekDay = isInteger(min=0, max=6), hour = isInteger(min=0, max=24)))

class isScheduler(isArray):
    
    def __init__(self):
        super(isScheduler, self).__init__(item = isSchedulerItem())


@attr('event', validator=isEvent(), model_adapter=EventAdapter(), description="The event object describing when to execute this rule")
@attr('enabled', validator=isBool(), default=True, description="If True (default), the rule is enabled")
@attr('scheduler', validator=isArray(item = isObject(start = isObject(weekDay = isInteger(min=0, max=6), hour = isInteger(min=0, max=24)), end = isObject(weekDay = isInteger(min=0, max=6), hour = isInteger(min=0, max=24)))), default=[], description="Activate this rule only within certain periods of time")
@attr('script', validator=isResource(accepted_types=('File',)), model_adapter=ResourceModelAdapter(), description="The JavaScript code to be executed")
@attr('script_args', validator=isString(), default='', description="The arguments passed to the script of this rule")
@attr('script_return_code', default=0, mode=READ_ONLY, description="The last exit code returned by the script of this rule")
@attr('script_execution_count', default=0, mode=READ_ONLY, description="The number of times this rule has been executed")
@attr('script_execution_date', default=None, mode=READ_ONLY, description="The last time this rule has been executed")
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

        script = self.script

        if script is None:
            raise Exception("the rules's script has been removed")

        self._script_execution_count = self.script_execution_count + 1

        self._script_execution_date = datetime.datetime.utcnow()

        try:
            result = ScriptEngine.runFromFile(script, arguments=self.script_args, globals={
                'signal': signal,
                'rule': self
            })
        except Exception as e:
            self._error = str(e)
            result = {}

        self._script_return_code = result.get('return_code', -1)

        stderr = result.get('stderr')
        if stderr:
            self.ething.log.error('rule %s error (return code = %d):' % (
                self, result.get('return_code')))
            self.ething.log.error(stderr)

        #stdout = result.get('stdout')
        # if stdout:
        #    self.ething.log.info(stdout)

        self.save()

        return result

    def __getattr__(self,    name):
        value = super(Rule, self).__getattr__(name)

        if name == 'script':
            return self.ething.get(value)
        else:
            return value
