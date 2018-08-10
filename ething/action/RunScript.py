# coding: utf-8

from .Action import Action
from ething.Resource import ResourceType
from ething.reg import *
from ething.ScriptEngine import ScriptEngine


@attr('script', type=ResourceType(accepted_types=('resources/File',)), description="The JavaScript code to be executed")
@attr('args', type=String(), default='', description="The arguments passed to the script")
@attr('return_code', default=0, mode=READ_ONLY, description="The last exit code returned by the script")
class RunScript(Action):

    def run(self, signal):
        script = self.script

        if script is None:
            raise Exception("the script has been removed")

        try:
            result = ScriptEngine.runFromFile(script, arguments=self.args, globals={
                'signal': signal,
                'rule': self.rule
            })
        except Exception as e:
            self.ething.log.exception('error in script')
            self._return_code = -1
        else:
            self._return_code = result.get('return_code', -1)

            stderr = result.get('stderr')
            if stderr:
                self.ething.log.error('rule %s error (return code = %d):' % (
                    self, result.get('return_code')))
                self.ething.log.error(stderr)

            # stdout = result.get('stdout')
            # if stdout:
            #    self.ething.log.info(stdout)

    def __getattr__(self, name):
        value = super(RunScript, self).__getattr__(name)

        if name == 'script':
            return self.ething.get(value)
        else:
            return value
