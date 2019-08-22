"""Stack tracer for multi-threaded applications.


Usage:

import stacktracer
stacktracer.start_trace("trace.html",interval=5,auto=True) # Set auto flag to always update file!
....
stacktracer.stop_trace()
"""

import sys
import traceback
import os
import time
import threading
from io import open

# Taken from http://bzimmer.ziclix.com/2008/12/17/python-thread-dumps/


def stacktraces():
    code = []
    threads = threading.enumerate()
    for threadId, stack in sys._current_frames().items():

        thread_name = ''
        for thread in threads:
            if thread.ident == threadId:
                thread_name = thread.name or ''
                break

        code.append("\n# ThreadID: %s, ThreadName: %s" % (threadId, thread_name))
        for filename, lineno, name, line in traceback.extract_stack(stack):
            code.append('File: "%s", line %d, in %s' % (filename, lineno, name))
            if line:
                code.append("  %s" % (line.strip()))

    return "\n".join(code)



class TraceDumper(threading.Thread):
    """Dump stack traces into a given file periodically."""

    def __init__(self, fpath, interval, auto, clean=True):
        """
        @param fpath: File path to output HTML (stack trace file)
        @param auto: Set flag (True) to update trace continuously.
            Clear flag (False) to update only if file not exists.
            (Then delete the file to force update.)
        @param interval: In seconds: how often to update the trace file.
        """
        assert (interval > 0.1)
        self.auto = auto
        self.clean = clean
        self.interval = interval
        self.fpath = os.path.abspath(fpath)
        self.stop_requested = threading.Event()
        threading.Thread.__init__(self)

    def run(self):
        while not self.stop_requested.isSet():
            time.sleep(self.interval)
            if self.auto or not os.path.isfile(self.fpath):
                self.stacktraces()

    def stop(self):
        self.stop_requested.set()
        self.join()
        try:
            if self.clean and os.path.isfile(self.fpath):
                os.unlink(self.fpath)
        except:
            pass

    def stacktraces(self):
        fout = open(self.fpath, "wb+")
        try:
            fout.write(stacktraces().encode('utf8'))
        finally:
            fout.close()


_tracer = None


def trace_start(fpath, interval=5, auto=True, clean=True):
    """Start tracing into the given file."""
    global _tracer
    if _tracer is None:
        _tracer = TraceDumper(fpath, interval, auto, clean)
        _tracer.setDaemon(True)
        _tracer.start()
    else:
        raise Exception("Already tracing to %s" % _tracer.fpath)


def trace_stop():
    """Stop tracing."""
    global _tracer
    if _tracer is None:
        raise Exception("Not tracing, cannot stop.")
    else:
        _tracer.stop()
        _tracer = None