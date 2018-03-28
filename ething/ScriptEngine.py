
	

from Helpers import dict_recursive_update, toJson

import os
import tempfile
import json
import time
import subprocess
import re
import shlex

def addslashes(s):
    l = ["\\", '"', "'", "\0", ]
    for i in l:
        if i in s:
            s = s.replace(i, '\\'+i)
    return s

class ScriptEngine(object):

	
	PROG = os.path.abspath(os.path.join(os.path.dirname(__file__), './nodejs/vm.js'))
	
	@staticmethod
	def run (ething, script, **options):
		
		nodejs_exe = core.config.get('nodejs.executable', None)
		
		if not nodejs_exe:
			raise Exception('execution of nodejs is disabled in the configuration')
		
		
		options = dict_recursive_update({
			'scriptName' : 'anonymous',
			'apiKey' : None,
			'globals' : None
		}, options)
		
		
		prog = ScriptEngine.PROG
		
		if not os.path.isfile(prog):
			raise Exception("unable to execute '%s'" % prog)
		
		# temporary files
		scriptHdl = tempfile.NamedTemporaryFile()
		scriptHdl.write(script)
		scriptHdl.flush()
		stdoutHdl = tempfile.NamedTemporaryFile()
		stderrHdl = tempfile.NamedTemporaryFile()
		resultHdl = tempfile.NamedTemporaryFile()
		
		cmd = [
			nodejs_exe,
			prog,
			scriptHdl.name,
			"--result",
			resultHdl.name,
			"--stdout",
			stdoutHdl.name,
			"--stderr",
			stderrHdl.name,
			"--apiUrl",
			addslashes('http://localhost:%d/api' % ething.config.get('webserver.port', 8000)),
			"-t",
			str(ething.config('script.timeout')),
			"--filename",
			options['scriptName']
		]
		
		if options['apiKey']:
			cmd.append('--apikey')
			cmd.append(options['apiKey'])
		else:
			cmd.append('--user')
			cmd.append('ething')
			cmd.append('--password')
			cmd.append('"%s"' % addslashes(ething.config('auth.password')))
		
		if isinstance(options['globals'], dict):
			cmd.append('--globals')
			cmd.append('"%s"' % addslashes(toJson(options['globals'])))
		
		cmd.append('2>&1');
		
		cmdstr = ' '.join(cmd)
		
		ething.log.debug("execute '%s'" % cmdstr)
		
		try:
			time_start = time.time()
			return_var = subprocess.call(cmdstr, shell=True);
			time_end = time.time()
			
			stdout = stdoutHdl.read()
			stderr = stderrHdl.read()
			result = resultHdl.read()
			
		except OSError as e:
			raise Exception('unable to execute nodejs [cmd=%s]' % nodejs_exe)
			
		finally:
			scriptHdl.close()
			stdoutHdl.close()
			stderrHdl.close()
			resultHdl.close()
		
		return {
			'executionTime' : time_end - time_start,
			'return' : result,
			'stdout' : stdout,
			'stderr' : stderr,
			'return_code': return_var,
			'ok' : return_var == 0
		}
	
	
	
	@staticmethod
	def runFromFile (script, arguments = ''):
		
		if script.mime != 'application/javascript':
			raise Exception('not a valid script file')
		
		scriptcontent = script.read()
		argv = []
		
		#if isinstance(script, Script):
		#	options['apiKey'] = script.apikey
		
		
		if isinstance(arguments, basestring) and len(arguments)>0:
			try:
				argv = shlex.split(arguments)
			except:
				pass
		
		globals = {
			'script' : script,
			'argv' : argv,
			'argc' : len(argv)
		}
		
		return ScriptEngine.run(script.ething, scriptcontent, scriptName = os.path.basename(script.name), globals = globals)
		
	
if __name__ == '__main__':
	
	from ething.core import Core
	
	core = Core({
		'db':{
			'database': 'test'
		},
		'log':{
			'level': 'debug'
		}
	})
	
	result = ScriptEngine.run(core, 'console.log("toto")');
	
	print result



