# coding: utf-8

import subprocess
import sys


def is_nodejs_installed(core=None):

    exe = "node"
    res = False

    if core:
        exe = core.config.get('nodejs.executable', None)

    if exe:
        try:
            res = subprocess.check_output(
                [exe, "--version"]).decode(sys.stdout.encoding or 'utf8').strip()
        except OSError as e:
            pass

    return res
