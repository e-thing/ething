# coding: utf-8

# load all the builtin plugins stored in this folder

import pkgutil
import os
import importlib


def find_builtin_plugins():
    plugins = []

    builtin_plugins_path = [os.path.dirname(__file__)]
    for loader, module_name, is_pkg in pkgutil.iter_modules(builtin_plugins_path):
        plugins.append(module_name)

    return plugins


def install_builtin_plugins(core):

    for module_name in find_builtin_plugins():
        try:
            mod = importlib.import_module('.%s' % module_name, __name__)
        except:
            core.log.exception('unable to import %s' % module_name)
        else:
            core.use(mod)