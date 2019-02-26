# coding: utf-8

"""
 @author Adrien Mezerette <a.mezerette@gmail.com>
 @package ething
"""
from __future__ import print_function

from .core.version import __version__

import argparse
import sys
import os
import errno
import time
import json
from io import open
import logging
from logging.handlers import RotatingFileHandler
import signal

from .core.env import USER_DIR, LOG_FILE, PID_FILE


# Default daemon parameters.
# File mode creation mask of the daemon.
UMASK = 0o177
# Default maximum for the number of available file descriptors.
MAXFD = 1024

def writePidFile():
    deletePidFile()
    pid = os.getpid()
    old_umask = os.umask(0o133)
    f = open(PID_FILE, "wb", encoding='utf8')
    f.write(str(pid))
    f.close()
    os.umask(old_umask)

def deletePidFile():
    if checkPidFile():
        os.remove(PID_FILE)

def checkPidFile():
    """ return pid as int or 0"""
    if os.path.isfile(PID_FILE):
        f = open(PID_FILE, "rb", encoding='utf8')
        pid = f.read().strip()
        f.close()
        if pid:
            return int(pid)
    return 0

def isAlreadyRunning():
    pid = checkPidFile()

    if pid and os.name != "nt":
        # check that the process still exists
        try:
            os.kill(pid, 0)  # 0 - default signal (does nothing)
        except OSError as e:  # the process exist but no access
            # if e.errno == errno.EACCES or e.errno == errno.EPERM:
            pass
        except:
            return 0  # the process does not exist anymore !

    return pid


def quitInstance():
    if os.name == "nt":
        print("Not supported on windows.")
        return

    pid = isAlreadyRunning()
    if not pid:
        print("No instance running.")
        return

    try:
        os.kill(pid, signal.SIGINT)  # SIGUIT

        t = time.time()
        print("waiting for ething to quit")

        while os.path.exists(PID_FILE) and t + 20 > time.time():
            time.sleep(0.25)

        if not os.path.exists(PID_FILE):
            print("ething successfully stopped")
        else:
            os.kill(pid, 9)  # SIGKILL
            print("ething did not respond")
            print("Kill signal was send to process with id %s" % pid)

    except Exception as e:
        print(e)
        print("Error quitting ething")


def createDaemon():
    """Detach a process from the controlling terminal and run it in the
    background as a daemon.
    Cf. http://code.activestate.com/recipes/278731-creating-a-daemon-the-python-way/
    """

    if os.name == 'nt':
        raise Exception("not available on windows")

    # The standard I/O file descriptors are redirected to /dev/null by default.
    if hasattr(os, "devnull"):
        REDIRECT_TO = os.devnull
    else:
        REDIRECT_TO = "/dev/null"

    try:
        # Fork a child process so the parent can exit.  This returns control to
        # the command-line or shell.  It also guarantees that the child will not
        # be a process group leader, since the child receives a new process ID
        # and inherits the parent's process group ID.  This step is required
        # to insure that the next call to os.setsid is successful.
        pid = os.fork()
    except OSError as e:
        raise Exception("%s [%d]" % (e.strerror, e.errno))

    if pid == 0:    # The first child.
        # To become the session leader of this new session and the process group
        # leader of the new process group, we call os.setsid(). The process is
        # also guaranteed not to have a controlling terminal.
        os.setsid()

        try:
            # Fork a second child and exit immediately to prevent zombies.
            pid = os.fork()
        except OSError as e:
            raise Exception("%s [%d]" % (e.strerror, e.errno))

        if pid == 0:    # The second child.
            # Since the current working directory may be a mounted filesystem, we
            # avoid the issue of not being able to unmount the filesystem at
            # shutdown time by changing it to the root directory.
            # os.chdir('/') # fail on import
            # We probably don't want the file mode creation mask inherited from
            # the parent, so we give the child complete control over permissions.
            os.umask(UMASK)
        else:
            os._exit(0)    # Exit parent (the first child) of the second child.
    else:
        os._exit(0)    # Exit parent of the first child.

    # Close all open file descriptors.  This prevents the child from keeping
    import resource        # Resource usage information.
    maxfd = resource.getrlimit(resource.RLIMIT_NOFILE)[1]
    if maxfd == resource.RLIM_INFINITY:
        maxfd = MAXFD

    for fd in range(0, maxfd):
        try:
            os.close(fd)
        except OSError:    # ERROR, fd wasn't open to begin with (ignored)
            pass

    os.open(REDIRECT_TO, os.O_RDWR)    # standard input (0)

    os.dup2(0, 1)            # standard output (1)
    os.dup2(0, 2)            # standard error (2)


def init_logger(console_log=False):

    frm = logging.Formatter("%(asctime)s :: %(name)s :: %(levelname)s :: %(message)s")
    log = logging.getLogger('ething')
    log.setLevel(logging.INFO)

    if console_log:
        console = logging.StreamHandler(sys.stdout)
        console.setFormatter(frm)
        log.addHandler(console)

    if not os.access(LOG_FILE, os.F_OK) or os.access(LOG_FILE, os.W_OK):
        # file_handler = logging.FileHandler(LOG_FILE, encoding="utf8")
        file_handler = RotatingFileHandler(LOG_FILE, encoding="utf8", maxBytes=10 * 1024 * 1024, backupCount=5)
        file_handler.setFormatter(frm)
        log.addHandler(file_handler)
        log.info('LOG_FILE = %s' % LOG_FILE)
    else:
        log.error('the log file is not writeable : %s' % LOG_FILE)

    return log


def remove_logger():
    log = logging.getLogger('ething')
    for h in list(log.handlers):
        log.removeHandler(h)
        h.close()


def destroy():
    if 'core' in globals():
        try:
            core.destroy()
        except:
            core.log.exception("exception in core.destroy()")

    try:
        remove_logger()
    except Exception as e:
        print("exception in remove_logger(): %s" % str(e))


def exit(status=None):
    destroy()
    sys.exit(status)


def main():

    global PID_FILE, core

    parser = argparse.ArgumentParser(
        description='Launch EThing home automation server.')

    parser.add_argument('-v', '--version', action='store_true',
                        help='return the version number and exit')
    parser.add_argument('-p', '--pidfile', type=str,
                        help='set pid to the given file')
    parser.add_argument('-q', '--quiet', action='store_true',
                            help='Quiet mode, disable log messages written to the terminal')

    if os.name != 'nt':
        # not available on windows !
        parser.add_argument('-d', '--daemon', action='store_true',
                            help='launch this program as a daemon')
        parser.add_argument('--stop', action='store_true',
                            help='stop any running instance and exit')

    parser.add_argument('--clear', action='store_true',
                        help='clear all the database and the configuration')

    parser.add_argument('--log-level', type=str,
                        help='set the log level')

    args = parser.parse_args()

    if args.version:
        print("v%s" % __version__)
        sys.exit()

    if getattr(args, 'pidfile', None) is not None:
        PID_FILE = args.pidfile

    if getattr(args, 'stop', None):
        quitInstance()
        sys.exit()

    if PID_FILE:
        try:
            pid = isAlreadyRunning()
        except IOError as e:
            pid = False
            if e.errno == errno.EACCES or e.errno == errno.EPERM:
                pid = True  # pid file exists but access denied

        if pid:
            print("ething already running with pid=%s" %
                  (str(pid) if pid is not True else '<access_denied>'))
            print("if it is not true, delete manually the file '%s' and try again." % PID_FILE)
            sys.exit(1)

    print("pid=%s" % os.getpid())

    if not os.path.exists(USER_DIR):
        # first start
        # some settup can be done here !
        print("first startup, initializing...")
        os.makedirs(USER_DIR)

    if getattr(args, 'daemon', None):
        createDaemon()

    from .core.utils import print_info

    log = init_logger(not (getattr(args, 'daemon', None) or getattr(args, 'quiet', False)))

    from .core import Core

    loglevel = getattr(args, 'log_level', None)
    if loglevel:
        loglevel = getattr(logging, loglevel.upper(), None)

    core = Core(clear_db=bool(args.clear), log_level=loglevel)

    print_info(core, core.log.info)

    # import builtin plugins here !
    from .plugins import install_builtin_plugins
    install_builtin_plugins(core)

    # import plugins
    from .core.plugin import find_plugins
    for module_name in find_plugins():
        core.use(module_name)

    core.init()

    exit_code = 0

    def stop(signum, frame):
        core.log.warning('signal received %d' % signum)
        if core.running:
            core.stop()

    signal.signal(signal.SIGINT, stop)
    signal.signal(signal.SIGTERM, stop)

    try:

        if PID_FILE:
            writePidFile()

        core.run()

    except KeyboardInterrupt:
        core.log.warning("killed ething from Terminal")

    except OSError as e:

        if e.errno == errno.EACCES or e.errno == errno.EPERM:
            core.log.exception(
                "Permission denied: you may need to execute this program with sudo")
            exit_code = 3
        elif e.errno == errno.EINTR:
            core.log.warning("interrupted")
            exit_code = 1
        else:
            core.log.exception("unexpected error")
            exit_code = 2

    except:
        core.log.exception("unexpected error")
        exit_code = 2

    finally:
        destroy()

        if PID_FILE:
            try:
                deletePidFile()
            except Exception as e:
                print("exception in deletePidFile(): %s" % str(e))

    if getattr(core, 'restart_flag', False):
        print("restarting...")
        python = sys.executable

        script=sys.argv[0]
        args = sys.argv[1:]

        if not os.path.isfile(script):
            script = 'ething'

        os.execl(python, python, script, *args)

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
