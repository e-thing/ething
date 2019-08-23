# coding: utf-8
from .. import *
import subprocess, shlex
import select
import gevent


@meta(icon="mdi-console", category="function")
@attr('timeout', type=Integer(min=0), default=0, description="Execution timeout in milliseconds")
@attr('output', type=Enum(('exec', 'spawn'), ('when the command is complete - exec mode', 'while the command is running - spawn mode')), default='exec')
@attr('extra_param', label="extra parameters", type=Descriptor(('string', 'msg', 'flow', 'glob', 'env')), default={'type':'string','value':''}, description="Extra parameters that will be appended to the command")
@attr('command', type=Descriptor(('string', 'msg', 'flow', 'glob', 'env')), default={'type':'string','value':''}, description="The command that is run")
class Exec(Node):
    INPUTS = ['default']
    OUTPUTS = ['default', 'stdout', 'stderr']

    def main(self, **inputs):
        _msg = inputs['default']
        _context = {
            'msg': _msg,
            'flow': self.flow,
        }

        cmd = "%s %s" % (self.command.get(**_context), self.extra_param.get(**_context))
        cmd = cmd.strip()

        if not cmd:
            return

        args = shlex.split(cmd)

        self.logger.debug('execute "%s"', cmd)

        p = subprocess.Popen(args, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        timeout = self.timeout
        if timeout > 0:
            timeout = timeout / 1000.
        else:
            timeout = None

        if self.output == 'exec':
            stdout, stderr = p.communicate(timeout=timeout)
            rc = p.returncode

            self.emit({
                'rc': rc,
                'payload': stdout
            }, 'stdout')

            if stderr:
                self.emit({
                    'rc': rc,
                    'payload': stderr
                }, 'stderr')

        else:

            def reader(p, pipe_name):
                pipe = getattr(p, pipe_name)
                for line in iter(pipe.readline, b''):
                    self.emit(line, pipe_name)

            gevent.joinall([
                gevent.spawn(reader, p, 'stdout'),
                gevent.spawn(reader, p, 'stderr')
            ], timeout=timeout, raise_error=(timeout is not None))

            #else: # does not work on windows
            #    t0 = time.time()
            #    while True:
            #
            #        time_left = None
            #        if timeout is not None:
            #            time_left = timeout - (time.time() - t0)
            #            if time_left <= 0:
            #                p.kill()
            #                p.wait()
            #                break
            #
            #        reads = [p.stdout.fileno(), p.stderr.fileno()]
            #        ret = select.select(reads, [], [], timeout=time_left)
            #
            #        for fd in ret[0]:
            #            if fd == p.stdout.fileno():
            #                read = p.stdout.readline()
            #                self.emit(read, 'stdout')
            #            if fd == p.stderr.fileno():
            #                read = p.stderr.readline()
            #                self.emit(read, 'stderr')
            #
            #        if p.poll() != None:
            #            break

            p.stdout.close()
            p.stderr.close()
            p.wait()

        self.emit({
            'payload': {
                'code': p.returncode
            }
        })

