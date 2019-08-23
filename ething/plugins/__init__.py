# coding: utf-8

# load all the builtin plugins stored in this folder

import pkgutil
import os
import importlib
import logging


LOGGER = logging.getLogger(__name__)


def find_builtin_plugins():
    plugins = []

    builtin_plugins_path = [os.path.dirname(__file__)]
    for loader, module_name, is_pkg in pkgutil.iter_modules(builtin_plugins_path):
        plugins.append(module_name)

    return plugins


def import_builtin_plugins(white_list=None):
    modules = list()

    for module_name in find_builtin_plugins():
        if white_list is None or module_name in white_list:
            try:
                mod = importlib.import_module('.%s' % module_name, __name__)
                modules.append(mod)
            except:
                LOGGER.exception('unable to import %s' % module_name)

    return modules


def install_builtin_plugins(core, **options):

    for module in import_builtin_plugins():
        core.use(module, **options.get(module.__name__, {}))
