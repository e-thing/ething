# coding: utf-8

from ething.core.Flow import ActionNode
from ething.core.Resource import ResourceType
from ething.core.reg import *


@attr('script', type=ResourceType(accepted_types=('resources/File',)), description="The JavaScript code to be executed")
@attr('args', type=String(), default='', description="The arguments passed to the script")
@attr('return_code', default=0, mode=READ_ONLY, description="The last exit code returned by the script")
class RunScript(ActionNode):

    def run(self, msg, core):
        script = core.get(self.script)

        if script is None:
            raise Exception("the script has been removed")

        try:
            result = core.get_plugin('JsScript').runFromFile(script, arguments=self.args, globals={
                'msg': msg
            })
        except Exception as e:
            self.log.exception('error in script')
            self.return_code = -1
        else:
            self.return_code = result.get('return_code', -1)

            stderr = result.get('stderr')
            if stderr:
                self.log.error('%s error (return code = %d):' % (
                    self, result.get('return_code')))
                self.log.error(stderr)

            # stdout = result.get('stdout')
            # if stdout:
            #    self.log.info(stdout)
