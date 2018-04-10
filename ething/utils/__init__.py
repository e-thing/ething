# coding: utf-8

from .pingable import pingable

from .nodejs import *

from .null_context_manager import NullContextManager


def print_info(core, printer):
    import platform, sys
    
    printer("ETHING    : version=%s" % core.version)
    
    printer("PYTHON    : version=%s type=%s" % (platform.python_version(), platform.python_implementation()))
    printer("PYTHON_EXE: %s" % (sys.executable))
    
    printer("PLATFORM  : %s %s" % (sys.platform, platform.platform()))
    printer("SYSTEM    : %s" % (platform.version()))
    
    printer("NODE.JS   : %s" % (is_nodejs_installed(core) or "not found"))
    
    
    
    

