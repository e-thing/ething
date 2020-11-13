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


def import_builtin_plugins(white_list=None, disabled=None):
    modules = list()

    for module_name in find_builtin_plugins():
        if disabled is None or module_name not in disabled:
            if white_list is None or module_name in white_list:
                try:
                    mod = importlib.import_module('.%s' % module_name, __name__)
                    modules.append(mod)
                except:
                    LOGGER.exception('unable to import %s' % module_name)
        else:
            LOGGER.info('plugin %s disabled' % module_name)

    return modules


def install_builtin_plugins(core, **options):

    for module in import_builtin_plugins():
        core.use(module, **options.get(module.__name__, {}))


def build_plugins_conf (fout):
    plugin_dir = os.path.dirname(__file__)
    for name in os.listdir(plugin_dir):
        d = os.path.join(plugin_dir, name)
        if os.path.isdir(d) and not name.startswith("__"):
            conf_file = os.path.join(d, "default.cfg")
            if os.path.isfile(conf_file):
                with open(conf_file) as f:
                    fout.write("\n")
                    for line in f:
                        fout.write(line)
