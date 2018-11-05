from ething.core.Helpers import topological_sort
import pkgutil
import traceback
import os
from io import open
import json
import importlib
from collections import OrderedDict
import inspect
import logging


class Plugin(object):

    def __init__(self, module, package = None):
        self._module = module
        self._package = package
        self._loaded_module = None
        self._info = {
            # the path to the plugin javascript file (metadata, widgets ...). This file is loaded by the web interface.
            'ui': './index.js',
            # the version of the plugin
            'version': None,
            # a string describing this plugin (default to the doc string of this class)
            'description': None,
            # the name of the plugin (default to the plugin class name)
            'name': self._module.name,
            # a dictionary object defining the default configuration of the plugin
            'config': None,
            # a json schema describing the configuration data. The web interface use this to create the configuration form
            'configSchema': None,
            # a list of other plugins that need to be loaded before this plugin
            'dependencies': []
        }
        self.load_plugin_json()

    def __getattr__(self, item):
        return self._info[item]

    def __str__(self):
        return '<plugin %s>' % self.name

    def __repr__(self):
        return str(self)

    def install(self, core):
        module_name = self._module.name

        if self._loaded_module is None:
            try:
                if self._package:
                    loaded_module = importlib.import_module('.%s' % module_name, self._package)
                else:
                    loaded_module = importlib.import_module(module_name)
            except Exception as e:
                print('plugin "%s" import failed: %s' % (self.name, str(e)))
                traceback.print_exc()
                return

            self._loaded_module = loaded_module

        for attr_name in dir(self._loaded_module):
            attr = getattr(self._loaded_module, attr_name)
            if inspect.isclass(attr) and issubclass(attr, PluginInstance) and attr is not PluginInstance:
                plugin_cls = attr
                try:
                    plugin_cls(core)
                except Exception as e:
                    print('plugin "%s" install failed: %s' % (self.name, str(e)))
                    traceback.print_exc()
                    return
                break
        else:
            if hasattr(self._loaded_module, 'install'):
                install_func = getattr(self._loaded_module, 'install')
                try:
                    install_func(core)
                except Exception as e:
                    print('plugin "%s" install failed: %s' % (self.name, str(e)))
                    traceback.print_exc()
                    return
            else:
                print('plugin "%s" no install function found nor plugin class found' % (self.name))

    def load_plugin_json(self):
        path = self._module.path
        directory = os.path.dirname(path)
        plugin_json_file = os.path.join(directory, 'plugin.json')

        try:
            if os.path.isfile(plugin_json_file):
                with open(plugin_json_file) as f:
                    self._info.update(json.load(f))
            else:
                print('plugin "%s" no plugin.json found' % (self.name))
        except:
            pass


class PluginInstance(object):
    """A plugin intance class"""

    def __init__(self, core):
        self.core = core
        self.log = logging.getLogger("ething.%s" % type(self).__name__)
        self.config = ConfigItem(core.config, self.name, schema = self.CONFIG_SCHEMA, defaults = copy.deepcopy(self.CONFIG_DEFAULTS))
        self.loaded = False

    @property
    def name(self):
        return self.NAME

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name

    def load(self):
        if self.loaded:
            raise Exception('plugin "%s" already loaded' % self)
        self.loaded = True
        self.log.info('load plugin version=%s' % str(self.VERSION))
        self.core.signalDispatcher.bind('ConfigUpdated', self._on_core_config_updated)

    def on_config_change(self):
        pass

    def _on_core_config_updated(self, signal):
        if self.name in signal.updated_keys:
            self.on_config_change()

    def export_data(self):
        pass

    def import_data(self, data):
        pass


_plugins_cache = None


def clear_cache():
    global _plugins_cache
    _plugins_cache = None


def find_plugins():
    global _plugins_cache

    if _plugins_cache is None:
        _plugins_cache = OrderedDict()

        # load builtin plugins
        builtin_plugins_path = [os.path.join(os.path.dirname(__file__), 'plugins')]
        for loader, module_name, is_pkg in pkgutil.iter_modules(builtin_plugins_path):
            module = loader.find_module(module_name)
            _plugins_cache[module_name] = Plugin(module, package='ething.plugins')

        # find installed packages in PYTHON_PATH
        for loader, module_name, is_pkg in pkgutil.iter_modules():
            if module_name.startswith('ething_'):
                module = loader.find_module(module_name)
                _plugins_cache[module_name] = Plugin(module)

    return [_plugins_cache[name] for name in _plugins_cache]


def install_plugins(core, include=None, exclude=None):

    plugins = find_plugins()

    selected = []

    if include is not None:
        for name in include:
            for p in plugins:
                if p.name == name:
                    selected.append(p)
                    break
    else:
        selected = plugins

    if exclude is not None:
        for name in exclude:
            for p in plugins:
                if p.name == name:
                    if p in selected:
                        selected.remove(p)
                    break

    # order by dependencies
    plugins_dep = []

    for p in selected:
        plugins_dep.append((p.name, p.dependencies or []))

    ordered_plugin_names = list(topological_sort(plugins_dep))

    for name in ordered_plugin_names:
        for p in selected:
            if p.name == name:
                p.install(core)
                break


if __name__ == '__main__':
    print('start')
    plugins = find_plugins()
    print(plugins)

    for p in plugins:
        print(p.name, p.version, p.description)
        p.install(None)
