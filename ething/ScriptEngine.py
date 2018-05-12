# coding: utf-8

from future.utils import string_types, text_type

from .Helpers import dict_recursive_update, toJson

import os
import tempfile
import json
import time
import subprocess
import re
import shlex
import sys
import json


def addslashes(s):
    l = ["\\", '"', "'", "\0", ]
    for i in l:
        if i in s:
            s = s.replace(i, '\\'+i)
    return s

class ScriptEngine(object):

    
    # PROG = os.path.abspath(os.path.join(os.path.dirname(__file__), './nodejs/vm.js'))
    PROG = os.path.abspath(os.path.join(os.path.dirname(__file__), './nodejs/vm2.js'))
    
    @staticmethod
    def run (ething, script, scriptName = 'anonymous', apiKey = None, globals = None):
        
        nodejs_exe = ething.config.get('nodejs.executable', None)
        
        if not nodejs_exe:
            raise Exception('execution of nodejs is disabled in the configuration')
        
        
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
            addslashes('http://localhost:%d' % ething.config.get('webserver.port', 8000)),
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
            cmd.append('"%s"' % addslashes(toJson(globals)))
        
        cmd.append('2>&1');
        
        cmdstr = ' '.join(cmd)
        
        ething.log.debug("execute '%s'" % cmdstr)
        
        try:
            time_start = time.time()
            return_var = subprocess.call(cmdstr, shell=True);
            time_end = time.time()
            
            out = outHdl.read()
            
        except OSError as e:
            raise Exception('unable to execute nodejs [cmd=%s]' % nodejs_exe)
            
        finally:
            scriptHdl.close()
            outHdl.close()
        
        out = out.decode(sys.stdout.encoding)
        
        if len(out):
            out = out[:out.rfind(',')]
        
        out = json.loads('[%s]' % out)
        
        sdterr = ''
        for item in out:
            if item['type'] == 'stderr':
                sdterr += item['chunk'].encode('utf8').decode('unicode_escape')
        
        try:
            result = json.loads(result)
        except:
            pass
        
        return {
            'executionTime' : time_end - time_start,
            'output' : out,
            'sdterr': sdterr,
            'return_code': return_var,
            'ok' : return_var == 0
        }
    
    
    
    @staticmethod
    def runFromFile (script, arguments = '', globals = {}):
        
        if script.mime != 'application/javascript':
            raise Exception('not a valid script file')
        
        scriptcontent = script.read()
        argv = []
        
        #if isinstance(script, Script):
        #    options['apiKey'] = script.apikey
        
        
        if isinstance(arguments, string_types) and len(arguments)>0:
            try:
                argv = shlex.split(arguments)
            except:
                pass
        
        if globals is None:
            globals = {}
        
        globals.update({
            'script' : script,
            'argv' : argv,
            'argc' : len(argv)
        })
        
        return ScriptEngine.run(script.ething, scriptcontent, scriptName = os.path.basename(script.name), globals = globals)
        
    

