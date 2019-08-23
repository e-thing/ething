# coding: utf-8

"""
 @author Adrien Mezerette <a.mezerette@gmail.com>
 @package ething
"""
from __future__ import print_function

from .version import __version__

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
import threading

from .env import USER_DIR, LOG_FILE


def init_logger(console_log=False, file_log=True, debug=False):
    from .utils.logger import ColoredFormatter

    frm = "%(asctime)s :: %(levelname)-7s :: %(name)s :: %(message)s"
    log = logging.getLogger('ething')
    log.setLevel(logging.DEBUG if debug else logging.INFO)

    if console_log:
        console = logging.StreamHandler(sys.stdout)
        console.setFormatter(ColoredFormatter(frm))
        log.addHandler(console)

    if file_log:
        if not os.access(LOG_FILE, os.F_OK) or os.access(LOG_FILE, os.W_OK):
            # file_handler = logging.FileHandler(LOG_FILE, encoding="utf8")
            file_handler = RotatingFileHandler(LOG_FILE, encoding="utf8", maxBytes=5 * 1024 * 1024, backupCount=2)
            file_handler.setFormatter(logging.Formatter(frm))
            log.addHandler(file_handler)
        else:
            log.error('the log file is not writeable : %s' % LOG_FILE)

    return log


def remove_logger(logger):
    for h in list(logger.handlers):
        logger.removeHandler(h)
        h.close()



parser = argparse.ArgumentParser(
    description='Launch EThing home automation server.')

parser.add_argument('-v', '--version', action='store_true',
                    help='return the version number and exit')

parser.add_argument('-q', '--quiet', action='store_true',
                    help='Quiet mode, disable log messages written to the terminal')

parser.add_argument('--debug', action='store_true',
                    help='activate the debug mode')

parser.add_argument('--clear', action='store_true',
                    help='clear all the database and the configuration')

parser.add_argument('--server-port', type=int, default=8000,
                    help='the port number the webserver is listening to')

parser.add_argument('--scan', action='store', nargs='?', type=int,
                    help='perform a scan of the system and exit')

args = parser.parse_args()

if args.version:
    print("v%s" % __version__)
    sys.exit()

if args.scan is not None:
    from .discovery import scan
    init_logger(console_log=True, file_log=False, debug=args.debug)
    timeout = args.scan or 10
    print('scanning ... timeout=%d' % timeout)
    scan(timeout=timeout, printer=print)
    sys.exit()

if not os.path.exists(USER_DIR):
    # first start
    # some settup can be done here !
    print("first startup, initializing...")
    os.makedirs(USER_DIR)

logger = init_logger(console_log=not getattr(args, 'quiet', False), file_log=True, debug=args.debug)

from .core import Core
from .processes import processes

core = Core(clear_db=bool(args.clear), debug=args.debug, webserver_port= args.server_port)

if args.debug:
    from .green import install_debugger
    install_debugger()

exit_code = 0

stop_evt = threading.Event()

def stop(signum, frame):
    logger.warning('signal received %d' % signum)
    stop_evt.set()

signal.signal(signal.SIGINT, stop)
signal.signal(signal.SIGTERM, stop)

try:
    stop_evt.wait()
except KeyboardInterrupt:
    logger.warning("killed ething from Terminal")
except OSError as e:

    if e.errno == errno.EACCES or e.errno == errno.EPERM:
        logger.exception(
            "Permission denied: you may need to execute this program with sudo")
        exit_code = 3
    elif e.errno == errno.EINTR:
        logger.warning("interrupted")
        exit_code = 1
    else:
        logger.exception("unexpected error")
        exit_code = 2

except:
    logger.exception("unexpected error")
    exit_code = 2

finally:
    core.close()

    try:
        processes.stop_all()
    except Exception as e:
        logger.exception("exception in processes.stop_all()")

    try:
        remove_logger(logger)
    except Exception as e:
        print("exception in remove_logger(): %s" % str(e))

sys.exit(exit_code)


