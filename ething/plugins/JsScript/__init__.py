# coding: utf-8

from future.utils import string_types, text_type
from ething.core.plugin import Plugin
from ething.core.Helpers import toJson
from .utils import addslashes, Output
from .RunScript import RunScript
from collections import OrderedDict
import os
import tempfile
import time
import subprocess
import re
import shlex
import sys
import json



PROG = os.path.abspath(os.path.join(os.path.dirname(__file__), './nodejs/vm2.js'))


class JsScript(Plugin):

    """
    JsScript plugin. This plugin allows you to execute JavaScript script using the ething-js library.
    """

    JS_INDEX = './js/index.js'

    CONFIG_DEFAULTS = {
        'executable': 'node',
        'timeout': 300000  # in millisecondes
    }

    CONFIG_SCHEMA = {
        'type': 'object',
        'properties': OrderedDict([
            ("executable", {
                "description": "node executable",
                "type": "string"
            }),
            ("timeout", {
                "description": "Script time limit expressed in milliseconds. 0 means unlimited.",
                "type": "integer",
                "minimum": 0
            })
        ])
    }

    def load(self):
        super(JsScript, self).load()

        self.log.info("NODE.JS : %s" % (self.is_nodejs_installed() or "not found"))

    def setup(self):
        # install specific http routes
        webserver_plugin = self.core.get_plugin('webserver')
        if webserver_plugin:
            webserver_plugin.register_installer(self._webserver_install)

    def run(self, script, scriptName='anonymous', apiKey=None, globals=None):

        nodejs_exe = self.config.get('executable', None)

        if not nodejs_exe:
            raise Exception(
                'nodejs is not configured')

        prog = PROG

        if not os.path.isfile(prog):
            raise Exception("unable to execute '%s'" % prog)

        if isinstance(script, text_type):
            script = script.encode('utf8')

        # temporary files
        scriptHdl = tempfile.NamedTemporaryFile()
        scriptHdl.write(script)
        scriptHdl.flush()
        outHdl = tempfile.NamedTemporaryFile()

        cmd = [
            nodejs_exe,
            prog,
            scriptHdl.name,
            "--out",
            outHdl.name,
            "--serverUrl",
            addslashes('http://localhost:%d' %
                       self.core.config.get('webserver.port', 8000)),
            "-t",
            str(self.config.get('timeout')),
            "--filename",
            scriptName
        ]

        if apiKey:
            cmd.append('--apikey')
            cmd.append(apiKey)

        if isinstance(globals, dict):
            cmd.append('--globals')
            cmd.append('%s' % toJson(toJson(globals)))

        cmd.append('2>&1')

        cmdstr = ' '.join(cmd)

        self.log.debug("execute '%s'" % cmdstr)

        try:
            time_start = time.time()
            return_var = subprocess.call(cmdstr, shell=True)
            time_end = time.time()

            out = outHdl.read()

        except OSError as e:
            raise Exception('unable to execute nodejs [cmd=%s]' % nodejs_exe)

        finally:
            scriptHdl.close()
            outHdl.close()

        out = out.decode(sys.stdout.encoding or 'utf8')

        self.log.debug("script return code : %d" % return_var)
        # self.log.debug("script stdout : %s" % out)

        if len(out):
            out = out[:out.rfind(',')]

        out = Output(json.loads('[%s]' % out))

        self.log.debug("script output : \n%s" % out.std)

        return {
            'executionTime': time_end - time_start,
            'output': out.chunked,
            'stderr': out.stderr,
            'out': out,
            'return_code': return_var,
            'ok': return_var == 0
        }

    def runFromFile(self, script, arguments='', globals=None):

        if script.mime != 'application/javascript':
            raise Exception('not a valid script file')

        scriptcontent = script.read()
        argv = []

        # if isinstance(script, Script):
        #    options['apiKey'] = script.apikey

        if isinstance(arguments, string_types) and len(arguments) > 0:
            try:
                argv = shlex.split(arguments)
            except:
                pass

        if globals is None:
            globals = {}

        args = OrderedDict()

        for arg in argv:
            m = re.search('^--?([^= ]+)(=(.*))?$', arg)
            if m:
                if m.group(2) is None:
                    args[m.group(1)] = True
                else:
                    args[m.group(1)] = m.group(3)
            else:
                args[arg] = True

        globals.update({
            'script': script,
            'argv': argv,
            'argc': len(argv),
            'args': args
        })

        return self.run(scriptcontent, scriptName=os.path.basename(script.name), globals=globals)

    def _webserver_install(self, app, auth, **kwargs):

        from ething.plugins.webserver.server_utils import use_args, fields

        file_action_execute_args = {
            'args': fields.Str(missing=None,
                               description="A string representing the arguments to be passed to the script.")
        }

        @app.route('/api/files/<id>/execute')
        @use_args(file_action_execute_args)
        @auth.required('file:read resource:read')
        def file_execute(args, id):

            r = app.getResource(id, ['File'])

            if r.mime == 'application/javascript':

                res = self.runFromFile(r, args['args'])

                if not res:
                    raise Exception('Unable to execute')

                return app.jsonify(res)

            else:
                raise Exception('Not executable')

    def is_nodejs_installed(self):
        res = False

        exe = self.config.get('executable', None)

        if exe:
            try:
                res = subprocess.check_output(
                    [exe, "--version"]).decode(sys.stdout.encoding or 'utf8').strip()
            except OSError as e:
                pass

        return res