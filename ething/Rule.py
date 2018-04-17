# coding: utf-8

from .Resource import Resource, isResource, ResourceModelAdapter
from .base import NestedAdapter, attr, READ_ONLY, isString, isAnything, isBool
from .ScriptEngine import ScriptEngine

from . import event



class isEvent(isAnything):
    
    def schema(self):
        return {"$ref":"Event"}


class EventAdapter(NestedAdapter):
    def __init__(self):
        super(EventAdapter, self).__init__(event.Event)
    
    def _inherit(self, data_object):
        return {
            'ething': data_object.ething
        }


@attr('event', validator = isEvent(), model_adapter = EventAdapter(), description="The event object describing when to execute this rule")
@attr('enabled', validator = isBool(), default = True, description="If True (default), the rule is enabled")
@attr('script', validator = isResource(accepted_types = ('File',)), model_adapter = ResourceModelAdapter(), description="The JavaScript code to be executed")
@attr('script_args', validator = isString(), default = '', description="The arguments passed to the script of this rule")
@attr('script_return_code', default = 0, mode = READ_ONLY, description="The last exit code returned by the script of this rule")
@attr('script_execution_count', default = 0, mode = READ_ONLY, description="The number of times this rule has been executed")
@attr('script_execution_date', default = None, mode = READ_ONLY, description="The last time this rule has been executed")
class Rule(Resource):
    
    
    def trigger(self, signal):
        
        if not self.event.filter(signal):
            return False
        
        return run(signal)
    
    
    def run(self, signal = None):
        
        script = self.script
        
        if script is None:
            raise Exception("the rules's script has been removed")
        
        self._script_execution_count = self.script_execution_count + 1
        
        try:
            result = ScriptEngine.runFromFile(script, arguments = self.script_args, globals = {
                'signal' : signal,
                'rule': self
            })
        except Exception as e:
            self._error = str(e)
        
        
        self._script_return_code = result.get('return_code')
        
        stderr = result.get('stderr')
        if stderr:
            self.ething.log.error('rule %s error:' % self)
            self.ething.log.error(stderr)
        
        self.save()
        
        return result
    
    
    def __getattr__ (self,    name ):
        value = super(Rule, self).__getattr__(name)
        
        if name == 'script':
            return self.ething.get(value)
        else:
            return value



