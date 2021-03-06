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

from .core.env import USER_DIR, LOG_FILE


def init_logger(console_log=False, debug=False):

    frm = logging.Formatter("%(asctime)s :: %(levelname)-7s :: %(name)s :: %(message)s")
    log = logging.getLogger()
    log.setLevel(logging.DEBUG if debug else logging.INFO)

    if console_log:
        console = logging.StreamHandler(sys.stdout)
        console.setFormatter(frm)
        log.addHandler(console)

    if not os.access(LOG_FILE, os.F_OK) or os.access(LOG_FILE, os.W_OK):
        # file_handler = logging.FileHandler(LOG_FILE, encoding="utf8")
        file_handler = RotatingFileHandler(LOG_FILE, encoding="utf8", maxBytes=5 * 1024 * 1024, backupCount=2)
        file_handler.setFormatter(frm)
        log.addHandler(file_handler)
    else:
        log.error('the log file is not writeable : %s' % LOG_FILE)

    return logging.getLogger('ething')


def remove_logger(logger):
    for h in list(logger.handlers):
        logger.removeHandler(h)
        h.close()


def main():

    global core

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

    parser.add_argument('--log-level', type=str,
                        help='set the log level')

    parser.add_argument('--server-port', type=int, default=8000,
                        help='the port number the webserver is listening to')

    args = parser.parse_args()

    if args.version:
        print("v%s" % __version__)
        sys.exit()

    if not os.path.exists(USER_DIR):
        # first start
        # some settup can be done here !
        print("first startup, initializing...")
        os.makedirs(USER_DIR)

    logger = init_logger(not getattr(args, 'quiet', False), args.debug)

    from .core import Core

    loglevel = getattr(args, 'log_level', None)
    if loglevel:
        loglevel = getattr(logging, loglevel.upper(), None)

    core = Core(clear_db=bool(args.clear), log_level=loglevel, debug=args.debug, logger=logger)

    # import builtin plugins here !
    logger.info('search for builtin plugins...')
    from .plugins import install_builtin_plugins
    install_builtin_plugins(core, webserver={'port': args.server_port})

    # import plugins
    logger.info('search for installed plugins...')
    from .core.plugin import find_plugins
    for module_name in find_plugins():
        try:
            core.use(module_name)
        except:
            logger.exception('unable to import %s' % module_name)

    exit_code = 0

    def stop(signum, frame):
        logger.warning('signal received %d' % signum)
        core.stop()

    signal.signal(signal.SIGINT, stop)
    signal.signal(signal.SIGTERM, stop)

    try:

        core.run()

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
        core.stop()

        try:
            core.destroy()
        except:
            logger.exception("exception in core.destroy()")

        try:
            remove_logger(logger)
        except Exception as e:
            print("exception in remove_logger(): %s" % str(e))

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
