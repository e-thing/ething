# coding: utf-8

from future.utils import string_types, text_type

from .Helpers import toJson

import os
import tempfile
import json
import time
import subprocess
import re
import shlex
import sys
import json
from collections import OrderedDict


def addslashes(s):
    l = ["\\", '"', "'", "\0", ]
    for i in l:
        if i in s:
            s = s.replace(i, '\\'+i)
    return s


class Output(object):

    def __init__(self, chunked_output):
        self._chunked_output = chunked_output
        # cached
        self._stderr = None
        self._stdout = None
        self._std = None

    def __str__(self):
        return self.std

    @property
    def chunked(self):
        return self._chunked_output

    @property
    def stderr(self):
        if self._stderr is None:
            self._stderr = self._cat('stderr')
        return self._stderr

    @property
    def stdout(self):
        if self._stdout is None:
            self._stdout = self._cat('stdout')
        return self._stdout

    @property
    def std(self):
        if self._std is None:
            self._std = self._cat()
        return self._std

    def _cat(self, type = None):
        strcat = ''
        for item in self._chunked_output:
            if type is not None and item['type'] != type:
                continue
            strcat += item['chunk'].encode('utf8').decode('unicode_escape', "replace")
        return strcat

class ScriptEngine(object):

    # PROG = os.path.abspath(os.path.join(os.path.dirname(__file__), './nodejs/vm.js'))
    PROG = os.path.abspath(os.path.join(
        os.path.dirname(__file__), './nodejs/vm2.js'))

    @staticmethod
    def run(ething, script, scriptName='anonymous', apiKey=None, globals=None):

        nodejs_exe = ething.config.get('nodejs.executable', None)

        if not nodejs_exe:
            raise Exception(
                'execution of nodejs is disabled in the configuration')

        prog = ScriptEngine.PROG

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
                       ething.config.get('webserver.port', 8000)),
            "-t",
            str(ething.config('script.timeout')),
            "--filename",
            scriptName
        ]

        if apiKey:
            cmd.append('--apikey')
            cmd.append(apiKey)
        # else:
        #     cmd.append('--user')
        #     cmd.append('"%s"' % addslashes(ething.config('auth.username')))
        #     cmd.append('--password')
        #     cmd.append('"%s"' % addslashes(ething.config('auth.password')))

        if isinstance(globals, dict):
            cmd.append('--globals')
            cmd.append('%s' % toJson(toJson(globals)))

        cmd.append('2>&1')

        cmdstr = ' '.join(cmd)

        ething.log.debug("execute '%s'" % cmdstr)

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
        
        ething.log.debug("script return code : %d" % return_var)
        # ething.log.debug("script stdout : %s" % out)

        if len(out):
            out = out[:out.rfind(',')]

        out = Output(json.loads('[%s]' % out))

        ething.log.debug("script output : \n%s" % out.std)

        return {
            'executionTime': time_end - time_start,
            'output': out.chunked,
            'stderr': out.stderr,
            'out': out,
            'return_code': return_var,
            'ok': return_var == 0
        }

    @staticmethod
    def runFromFile(script, arguments='', globals=None):

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

        return ScriptEngine.run(script.ething, scriptcontent, scriptName=os.path.basename(script.name), globals=globals)
